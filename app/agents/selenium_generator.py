import ast
import json
import logging

from app.core.ai_client import ai_client
from app.core.prompt_loader import load_prompt

from app.schemas.testcase_schema import TestCaseList
from app.schemas.selenium_schema import SeleniumScriptList

from app.services.dom_service import DOMService


logger = logging.getLogger(__name__)


class SeleniumGenerator:

    # --------------------------------------------------
    # Per-script quality checks
    # --------------------------------------------------

    @staticmethod
    def validate_script_quality(
        code: str,
        application_url: str,
        dom_information: dict
    ) -> list[str]:
        """
        Return a list of problems for one script.
        Empty list means the script is acceptable.
        """

        errors = []

        # ----- URL checks -----

        for forbidden in ["example.com", "localhost", "127.0.0.1"]:
            if forbidden in code:
                errors.append(f"Forbidden URL detected: {forbidden}")

        if application_url not in code:
            errors.append("Application URL not used.")

        # ----- Placeholder checks -----

        for placeholder in [
            "REPLACE_USERNAME",
            "REPLACE_PASSWORD",
            "REPLACE_WITH_ACTUAL_LOCATOR",
        ]:
            if placeholder in code:
                errors.append(f"Placeholder detected: {placeholder}")

        # ----- Feature hallucination checks -----

        dom_json = json.dumps(dom_information).lower()

        for feature in ["registration", "signup", "checkout", "payment"]:
            if feature in code.lower() and feature not in dom_json:
                errors.append(
                    f"Unsupported feature generated: {feature}"
                )

        # ----- Fragile locator patterns -----

        if "contains(text()" in code:
            errors.append(
                "Fragile locator contains(text(), ...) used — "
                "must use normalize-space() instead."
            )

        # ----- Required components -----

        for item in ["driver.quit()", "WebDriverWait", "assert"]:
            if item not in code:
                errors.append(f"Missing required component: {item}")

        # ----- Structure: code must live inside a pytest function -----
        # Module-level Selenium code runs at pytest collection time
        # and breaks the whole run (exit code 2).

        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Syntax problems are handled (and repaired) separately.
            return errors

        has_test_function = any(
            isinstance(node, ast.FunctionDef)
            and node.name.startswith("test_")
            for node in tree.body
        )

        if not has_test_function:
            errors.append(
                "No pytest test function (def test_...) found."
            )

        allowed_toplevel = (
            ast.Import,
            ast.ImportFrom,
            ast.FunctionDef,
            ast.ClassDef,
            ast.Assign,          # constants like USERNAME = ...
            ast.AnnAssign,
        )

        for node in tree.body:
            if not isinstance(node, allowed_toplevel):
                errors.append(
                    "Executable code found at module level "
                    "(must be inside the test function)."
                )
                break

        return errors

    # --------------------------------------------------
    # Main generation
    # --------------------------------------------------

    @staticmethod
    def generate(
        test_cases: TestCaseList,
        application_url: str
    ) -> SeleniumScriptList:

        # ----- Validate URL -----

        if not application_url or not application_url.strip():
            raise ValueError("Application URL is required.")

        application_url = application_url.strip()

        logger.info("APPLICATION URL: %s", application_url)

        # ----- Analyze website DOM -----

        logger.info("ANALYZING WEBSITE DOM...")

        dom_information = DOMService.analyze(application_url)

        logger.info(
            "DOM INFORMATION:\n%s",
            json.dumps(dom_information, indent=2)
        )

        # ----- Build prompt -----

        prompt = load_prompt("selenium_prompt.txt")
        prompt = prompt.replace("{application_url}", application_url)
        prompt = prompt.replace(
            "{dom_information}",
            json.dumps(dom_information, indent=2)
        )
        prompt = prompt.replace(
            "{test_cases}",
            json.dumps(test_cases.model_dump(), indent=2)
        )

        # ----- Generate -----

        raw = ai_client.generate_structured(
            prompt=prompt,
            schema=dict
        )

        # ----- Normalize response shape -----

        if isinstance(raw, dict):
            if "scripts" not in raw:
                raise Exception(
                    "LLM response does not contain 'scripts'."
                )
            normalized = raw
        elif isinstance(raw, list):
            normalized = {"scripts": raw}
        else:
            raise Exception(f"Unexpected AI response:\n{raw}")

        selenium_scripts = SeleniumScriptList.model_validate(normalized)

        if len(selenium_scripts.scripts) == 0:
            raise Exception("No Selenium scripts were generated.")

        logger.info(
            "TOTAL SCRIPTS GENERATED: %d",
            len(selenium_scripts.scripts)
        )

        # ==============================================
        # Validate each script.
        # Invalid scripts are SKIPPED (with a logged
        # reason) instead of failing the whole batch.
        # ==============================================

        valid_scripts = []
        skipped = []
        filenames = set()

        for script in selenium_scripts.scripts:

            # ----- Normalize file name -----

            if not script.file_name.startswith("test_"):
                script.file_name = f"test_{script.file_name}"

            if not script.file_name.endswith(".py"):
                script.file_name += ".py"

            logger.info("PROCESSING: %s", script.file_name)

            # ----- Strip markdown fences -----

            code = (
                script.code
                .replace("```python", "")
                .replace("```", "")
                .strip()
            )

            # ----- Syntax check (with AI repair) -----

            try:
                ast.parse(code)
            except SyntaxError as e:
                logger.warning(
                    "Syntax error in %s — attempting repair: %s",
                    script.file_name, e
                )
                try:
                    repaired = ai_client.repair_python(code, str(e))
                    repaired = (
                        repaired
                        .replace("```python", "")
                        .replace("```", "")
                        .strip()
                    )
                    ast.parse(repaired)
                    code = repaired
                    logger.info("REPAIR SUCCESSFUL: %s", script.file_name)
                except Exception as repair_error:
                    skipped.append({
                        "file": script.file_name,
                        "reason": f"Unrepairable syntax error: {repair_error}"
                    })
                    continue

            # ----- Quality checks -----

            quality_errors = SeleniumGenerator.validate_script_quality(
                code,
                application_url,
                dom_information
            )

            if quality_errors:
                skipped.append({
                    "file": script.file_name,
                    "reason": "; ".join(quality_errors)
                })
                logger.warning(
                    "SKIPPING %s: %s",
                    script.file_name,
                    "; ".join(quality_errors)
                )
                continue

            # ----- Duplicate names -----

            if script.file_name in filenames:
                skipped.append({
                    "file": script.file_name,
                    "reason": "Duplicate filename."
                })
                continue

            filenames.add(script.file_name)

            script.code = code.rstrip() + "\n"
            valid_scripts.append(script)

            logger.info("SCRIPT VALIDATED: %s", script.file_name)

        # ==============================================
        # Summary
        # ==============================================

        logger.info("=" * 60)
        logger.info("SELENIUM GENERATION SUMMARY")
        logger.info("Valid scripts   : %d", len(valid_scripts))
        logger.info("Skipped scripts : %d", len(skipped))
        for item in skipped:
            logger.info("  SKIPPED %s — %s", item["file"], item["reason"])
        logger.info("=" * 60)

        if not valid_scripts:
            details = "\n".join(
                f"- {item['file']}: {item['reason']}" for item in skipped
            )
            raise Exception(
                "All generated scripts were invalid:\n" + details
            )

        return SeleniumScriptList(scripts=valid_scripts)
