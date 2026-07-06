import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

GENERATED_TESTS = Path("generated_tests")
REPORTS = Path("reports")
HISTORY_FILE = REPORTS / "history.json"
LAST_RUN_FILE = REPORTS / "last_run.json"
MAX_HISTORY_ENTRIES = 100


def parse_pytest_summary(stdout: str) -> dict:
    """
    Extract pass/fail/skip counts from a pytest summary line like:
    '==== 2 failed, 3 passed, 1 skipped in 42.31s ===='
    """

    counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}

    for key in counts:
        match = re.search(rf"(\d+) {key.rstrip('s')}", stdout)
        if match:
            counts[key] = int(match.group(1))

    return counts


def parse_failed_tests(stdout: str) -> list[str]:
    """
    Extract failing test file paths from pytest output lines like:
    'FAILED generated_tests/test_login.py::test_login - AssertionError'
    """

    files = []

    for match in re.finditer(r"FAILED ([^\s:]+\.py)", stdout):
        path = match.group(1)
        if path not in files:
            files.append(path)

    return files


class ExecutionService:

    @staticmethod
    def execute():

        REPORTS.mkdir(exist_ok=True)

        report_file = REPORTS / "report.html"

        # ----------------------------------------
        # Validate generated tests
        # ----------------------------------------

        if not GENERATED_TESTS.exists():
            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": "generated_tests folder not found.",
                "report": ""
            }

        test_files = list(GENERATED_TESTS.glob("test_*.py"))

        if not test_files:
            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": "No Selenium test scripts found.",
                "report": ""
            }

        # ----------------------------------------
        # Run pytest
        # ----------------------------------------

        command = [
            "pytest",
            str(GENERATED_TESTS),
            "-v",
            "--tb=long",
            f"--html={report_file}",
            "--self-contained-html"
        ]

        started = time.time()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=900
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": "Test execution timed out after 15 minutes.",
                "report": ""
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "report": ""
            }

        duration = round(time.time() - started, 2)

        counts = parse_pytest_summary(result.stdout)
        failed_files = parse_failed_tests(result.stdout)

        response = {
            "status": "SUCCESS" if result.returncode == 0 else "FAILED",
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "report": str(report_file),
            "duration_seconds": duration,
            "passed": counts["passed"],
            "failed": counts["failed"],
            "skipped": counts["skipped"],
            "failed_files": failed_files,
        }

        ExecutionService._record_history(response)

        return response

    # ----------------------------------------
    # History persistence
    # ----------------------------------------

    @staticmethod
    def _record_history(response: dict):

        try:

            entry = {
                "timestamp": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                ),
                "status": response["status"],
                "return_code": response["return_code"],
                "passed": response["passed"],
                "failed": response["failed"],
                "skipped": response["skipped"],
                "duration_seconds": response["duration_seconds"],
            }

            history = []

            if HISTORY_FILE.exists():
                try:
                    history = json.loads(
                        HISTORY_FILE.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    history = []

            history.append(entry)
            history = history[-MAX_HISTORY_ENTRIES:]

            HISTORY_FILE.write_text(
                json.dumps(history, indent=2),
                encoding="utf-8"
            )

            # Persist the full last run (needed by self-healing)
            LAST_RUN_FILE.write_text(
                json.dumps(response, indent=2),
                encoding="utf-8"
            )

        except Exception:
            # History must never break test execution.
            pass
