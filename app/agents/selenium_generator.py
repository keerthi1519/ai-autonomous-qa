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

    @staticmethod
    def validate_script_quality(
        code: str,
        application_url: str
    ):

        errors = []

        # ----------------------------------------
        # URL Validation
        # ----------------------------------------

        if "https://example.com" in code:
            errors.append("example.com detected.")

        if "http://example.com" in code:
            errors.append("example.com detected.")

        if application_url not in code:
            errors.append(
                "Application URL not used."
            )

        # ----------------------------------------
        # Credentials
        # ----------------------------------------

        if "REPLACE_USERNAME" in code:
            errors.append(
                "Placeholder username detected."
            )

        if "REPLACE_PASSWORD" in code:
            errors.append(
                "Placeholder password detected."
            )

        # ----------------------------------------
        # Fake Locator
        # ----------------------------------------

        if "REPLACE_WITH_ACTUAL_LOCATOR" in code:
            errors.append(
                "Placeholder locator detected."
            )

        # ----------------------------------------
        # Unsupported Feature
        # ----------------------------------------

        unsupported = [
            "registration",
            "signup",
            "checkout",
            "payment"
        ]

        for feature in unsupported:

            if feature in code.lower():

                errors.append(
                    f"Unsupported feature generated: {feature}"
                )

        return errors

    @staticmethod
    def generate(
        test_cases: TestCaseList,
        application_url: str
    ) -> SeleniumScriptList:

        # ==============================================
        # Validate URL
        # ==============================================

        if not application_url:
            raise ValueError(
                "Application URL is required."
            )

        application_url = application_url.strip()

        if application_url == "":
            raise ValueError(
                "Application URL cannot be empty."
            )

        logger.info("=" * 80)
        logger.info("APPLICATION URL")
        logger.info(application_url)
        logger.info("=" * 80)

        # ==============================================
        # Analyze Website DOM
        # ==============================================

        logger.info("=" * 80)
        logger.info("ANALYZING WEBSITE DOM")
        logger.info("=" * 80)

        dom_information = DOMService.analyze(
            application_url
        )

        logger.info("=" * 80)
        logger.info("DOM INFORMATION")
        logger.info("=" * 80)

        logger.info(
            json.dumps(
                dom_information,
                indent=2
            )
        )

        # ==============================================
        # Load Prompt
        # ==============================================

        prompt = load_prompt(
            "selenium_prompt.txt"
        )

        prompt = prompt.replace(
            "{application_url}",
            application_url
        )

        prompt = prompt.replace(
            "{dom_information}",
            json.dumps(
                dom_information,
                indent=2
            )
        )

        prompt = prompt.replace(
            "{test_cases}",
            json.dumps(
                test_cases.model_dump(),
                indent=2
            )
        )

        logger.info("=" * 80)
        logger.info("FINAL PROMPT")
        logger.info("=" * 80)
        logger.info(prompt)

        # ==============================================
        # Generate Structured Output
        # ==============================================

        raw = ai_client.generate_structured(
            prompt=prompt,
            schema=dict
        )

        logger.info("=" * 80)
        logger.info("RAW AI RESPONSE")
        logger.info("=" * 80)

        logger.info(
            json.dumps(
                raw,
                indent=2
            )
        )
        
                # ==============================================
        # Normalize Response
        # ==============================================

        if isinstance(raw, dict):

            if "scripts" not in raw:

                raise Exception(
                    "LLM response does not contain 'scripts'."
                )

            normalized = raw

        elif isinstance(raw, list):

            normalized = {
                "scripts": raw
            }

        else:

            raise Exception(
                f"Unexpected AI response:\n{raw}"
            )

        # ==============================================
        # Validate Schema
        # ==============================================

        selenium_scripts = SeleniumScriptList.model_validate(
            normalized
        )

        if len(selenium_scripts.scripts) == 0:

            raise Exception(
                "No Selenium scripts were generated."
            )

        logger.info("=" * 80)
        logger.info(
            "TOTAL SCRIPTS GENERATED : %d",
            len(selenium_scripts.scripts)
        )
        logger.info("=" * 80)

        # ==============================================
        # Validate Each Script
        # ==============================================

        for script in selenium_scripts.scripts:

            logger.info("=" * 80)
            logger.info(
                "PROCESSING : %s",
                script.file_name
            )
            logger.info("=" * 80)

            # ------------------------------------------
            # Normalize File Name
            # ------------------------------------------

            if not script.file_name.startswith(
                "test_"
            ):

                script.file_name = (
                    f"test_{script.file_name}"
                )

            if not script.file_name.endswith(
                ".py"
            ):

                script.file_name += ".py"

            # ------------------------------------------
            # Remove Markdown
            # ------------------------------------------

            code = (
                script.code
                .replace(
                    "```python",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

            logger.info(
                "SCRIPT CLEANED SUCCESSFULLY"
            )

            # ------------------------------------------
            # Quality Validation
            # ------------------------------------------

            quality_errors = (
                SeleniumGenerator.validate_script_quality(
                    code,
                    application_url
                )
            )

            if quality_errors:

                raise Exception(
                    f"""

Invalid Selenium Script

File:
{script.file_name}

Problems:

{chr(10).join(quality_errors)}

Generated Code:

{code}

"""
                )

            logger.info(
                "QUALITY VALIDATION PASSED"
            )

            # ------------------------------------------
            # Validate Python Syntax
            # ------------------------------------------

            try:

                ast.parse(code)

                logger.info(
                    "PYTHON SYNTAX VALID"
                )
            except SyntaxError as e:

                logger.error("=" * 80)
                logger.error("INVALID PYTHON GENERATED")
                logger.error("FILE : %s", script.file_name)
                logger.error("ERROR : %s", str(e))
                logger.error("=" * 80)

                logger.info(
                    "ATTEMPTING AUTOMATIC REPAIR..."
                )

                try:

                    repaired = ai_client.repair_python(
                        code,
                        str(e)
                    )

                    repaired = (
                        repaired
                        .replace(
                            "```python",
                            ""
                        )
                        .replace(
                            "```",
                            ""
                        )
                        .strip()
                    )

                    logger.info(
                        "REPAIRED PYTHON RECEIVED"
                    )

                    # --------------------------------------
                    # Validate repaired code
                    # --------------------------------------

                    ast.parse(repaired)

                    logger.info(
                        "REPAIR SUCCESSFUL"
                    )

                    code = repaired

                except Exception as repair_error:

                    logger.exception(
                        "AUTOMATIC REPAIR FAILED"
                    )

                    raise Exception(
                        f"""

Unable to repair generated Python.

File:
{script.file_name}

Original Error:
{e}

Repair Error:
{repair_error}

Generated Code:

{code}

"""
                    )

            # ------------------------------------------
            # Final URL Validation
            # ------------------------------------------

            if "example.com" in code:

                raise Exception(
                    f"""

Invalid Selenium Script

File:
{script.file_name}

Reason:
example.com still exists.

"""
                )

            if application_url not in code:

                raise Exception(
                    f"""

Invalid Selenium Script

File:
{script.file_name}

Reason:
Application URL missing.

Expected URL:

{application_url}

"""
                )

            logger.info(
                "URL VALIDATION PASSED"
            )

            # ------------------------------------------
            # Final Python Validation
            # ------------------------------------------

            try:

                ast.parse(code)

            except SyntaxError as e:

                raise Exception(
                    f"""

Final Python validation failed.

File:
{script.file_name}

Error:

{e}

Generated Code:

{code}

"""
                )

            logger.info(
                "FINAL PYTHON VALIDATION PASSED"
            )

            # ------------------------------------------
            # Required Selenium Components
            # ------------------------------------------

            required = [
                "driver.quit()",
                "WebDriverWait",
                "assert"
            ]

            for item in required:

                if item not in code:

                    raise Exception(
                        f"""

File:
{script.file_name}

Missing Required Component:

{item}

"""
                    )

            logger.info(
                "REQUIRED COMPONENT VALIDATION PASSED"
            )
                        # ------------------------------------------
            # DOM Validation
            # ------------------------------------------

            logger.info("=" * 80)
            logger.info("DOM VALIDATION")
            logger.info("=" * 80)

            dom_json = json.dumps(
                dom_information
            ).lower()

            # Prevent AI from inventing obvious features
            unsupported_features = [
                "registration",
                "signup",
                "checkout",
                "payment"
            ]

            for feature in unsupported_features:

                if (
                    feature in code.lower()
                    and feature not in dom_json
                ):

                    raise Exception(
                        f"""

Generated Selenium uses unsupported feature.

Feature:
{feature}

File:
{script.file_name}

"""
                    )

            logger.info(
                "DOM FEATURE VALIDATION PASSED"
            )

            # ------------------------------------------
            # Prevent Placeholder URLs
            # ------------------------------------------

            forbidden = [
                "example.com",
                "localhost",
                "127.0.0.1"
            ]

            for url in forbidden:

                if url in code:

                    raise Exception(
                        f"""

Forbidden URL detected.

File:
{script.file_name}

URL:
{url}

"""
                    )

            logger.info(
                "URL VALIDATION PASSED"
            )

            # ------------------------------------------
            # Final Formatting
            # ------------------------------------------

            code = code.rstrip() + "\n"

            script.code = code

            logger.info("=" * 80)
            logger.info(
                "FINAL SCRIPT : %s",
                script.file_name
            )
            logger.info("=" * 80)

            logger.info(script.code)

            logger.info("=" * 80)
            logger.info(
                "SCRIPT VALIDATED SUCCESSFULLY"
            )
            logger.info("=" * 80)

        # ==============================================
        # Final Validation
        # ==============================================

        filenames = set()

        for script in selenium_scripts.scripts:

            if script.file_name in filenames:

                raise Exception(
                    f"Duplicate filename detected: {script.file_name}"
                )

            filenames.add(script.file_name)

        logger.info("=" * 80)
        logger.info("ALL GENERATED SCRIPTS VALIDATED")
        logger.info("=" * 80)
                # ==============================================
        # Final Summary
        # ==============================================

        logger.info("=" * 80)
        logger.info("SELENIUM GENERATION SUMMARY")
        logger.info("=" * 80)

        logger.info(
            "Application URL : %s",
            application_url
        )

        logger.info(
            "Total Scripts : %d",
            len(selenium_scripts.scripts)
        )

        logger.info("Generated Files:")

        for script in selenium_scripts.scripts:

            logger.info(
                "  • %s",
                script.file_name
            )

        logger.info("=" * 80)
        logger.info("SELENIUM GENERATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return selenium_scripts