import subprocess
from pathlib import Path


class ExecutionService:

    @staticmethod
    def execute():

        # ----------------------------------------
        # Directories
        # ----------------------------------------

        generated_tests = Path("generated_tests")
        reports = Path("reports")

        reports.mkdir(exist_ok=True)

        report_file = reports / "report.html"

        # ----------------------------------------
        # Validate generated tests
        # ----------------------------------------

        if not generated_tests.exists():

            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": "generated_tests folder not found.",
                "report": ""
            }

        test_files = list(generated_tests.glob("test_*.py"))

        if not test_files:

            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": "No Selenium test scripts found.",
                "report": ""
            }

        # ----------------------------------------
        # Pytest Command
        # ----------------------------------------

        command = [
            "pytest",
            str(generated_tests),
            "-v",
            "--tb=long",
            f"--html={report_file}",
            "--self-contained-html"
        ]

        print("=" * 80)
        print("Executing Command")
        print(" ".join(command))
        print("=" * 80)

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

        except Exception as e:

            return {
                "status": "FAILED",
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "report": ""
            }

        print("=" * 80)
        print("STDOUT")
        print(result.stdout)
        print("=" * 80)

        print("=" * 80)
        print("STDERR")
        print(result.stderr)
        print("=" * 80)

        print("Return Code:", result.returncode)

        return {

            "status": "SUCCESS" if result.returncode == 0 else "FAILED",

            "return_code": result.returncode,

            "stdout": result.stdout,

            "stderr": result.stderr,

            "report": str(report_file)

        }