import ast
import json
import logging
import re
from pathlib import Path

from app.core.ai_client import ai_client
from app.services.execution_service import ExecutionService, LAST_RUN_FILE

logger = logging.getLogger(__name__)


class HealingService:
    """
    Self-healing test runner.

    Reads the last execution result, asks the AI to repair each
    failing script using its actual runtime error, then re-runs
    the test suite.
    """

    @staticmethod
    def heal_and_rerun() -> dict:

        # ----------------------------------------
        # Load last run
        # ----------------------------------------

        if not LAST_RUN_FILE.exists():
            raise ValueError(
                "No previous execution found. Run the tests first."
            )

        last_run = json.loads(
            LAST_RUN_FILE.read_text(encoding="utf-8")
        )

        failed_files = last_run.get("failed_files", [])

        if not failed_files:
            raise ValueError(
                "The last run has no failing tests to heal."
            )

        stdout = last_run.get("stdout", "")

        # ----------------------------------------
        # Heal each failed script
        # ----------------------------------------

        healed = []
        unhealed = []

        for file_path in failed_files:

            path = Path(file_path)

            if not path.exists():
                unhealed.append({
                    "file": file_path,
                    "reason": "File not found."
                })
                continue

            code = path.read_text(encoding="utf-8")

            error_context = HealingService._extract_error(
                stdout, path.name
            )

            logger.info("HEALING: %s", path.name)

            try:
                fixed = HealingService._repair_with_ai(
                    code, error_context
                )
                path.write_text(fixed, encoding="utf-8")
                healed.append(path.name)
                logger.info("HEALED: %s", path.name)
            except Exception as e:
                logger.exception("Healing failed for %s", path.name)
                unhealed.append({
                    "file": path.name,
                    "reason": str(e)
                })

        # ----------------------------------------
        # Re-run the suite
        # ----------------------------------------

        result = ExecutionService.execute()

        result["healed_files"] = healed
        result["unhealed_files"] = unhealed

        return result

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    @staticmethod
    def _extract_error(stdout: str, filename: str) -> str:
        """
        Pull the traceback section for one test file out of
        the full pytest output (best effort).
        """

        pattern = rf"_{{2,}} \S*{re.escape(filename.replace('.py', ''))}\S* _{{2,}}(.*?)(?=_{{2,}} |\Z)"

        match = re.search(pattern, stdout, re.DOTALL)

        if match:
            return match.group(1)[:3000]

        return stdout[-3000:]

    @staticmethod
    def _repair_with_ai(code: str, error: str) -> str:

        prompt = f"""
You are an expert Selenium QA engineer.

The following pytest + Selenium test failed at RUNTIME.

Fix the script so it passes. You MAY change locators, waits,
and assertions to match how the page actually behaves.
You may NOT change the target URL or the purpose of the test.

Rules:
1. Keep the pytest structure: all code inside def test_xxx().
2. Keep imports at the top.
3. Prefer robust locators: By.ID, By.NAME,
   CSS like "button[type='submit']",
   or XPath with normalize-space().
4. Never use contains(text(), ...).
5. Use WebDriverWait for anything that loads or changes.
6. Return ONLY the complete fixed Python file.
7. No markdown. No explanations.

RUNTIME ERROR:

{error}

CURRENT SCRIPT:

{code}
"""

        fixed = ai_client.generate(prompt)

        fixed = (
            fixed
            .replace("```python", "")
            .replace("```", "")
            .strip()
        )

        if not fixed:
            raise Exception("AI returned an empty script.")

        # Must be valid Python with a pytest function
        tree = ast.parse(fixed)

        has_test = any(
            isinstance(node, ast.FunctionDef)
            and node.name.startswith("test_")
            for node in tree.body
        )

        if not has_test:
            raise Exception(
                "Repaired script has no pytest test function."
            )

        return fixed.rstrip() + "\n"
