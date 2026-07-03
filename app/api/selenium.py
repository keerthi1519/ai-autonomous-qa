from pathlib import Path
import ast
import traceback

from fastapi import APIRouter, HTTPException

from app.agents.selenium_generator import SeleniumGenerator
from app.schemas.selenium_request_schema import SeleniumRequest

router = APIRouter(
    tags=["Selenium"]
)

# ------------------------------------------
# Backend Generated Tests Folder
# ------------------------------------------

GENERATED_TESTS_DIR = Path("generated_tests")
GENERATED_TESTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/generate-selenium")
async def generate_selenium(
    request: SeleniumRequest
):

    try:

        print("=" * 80)
        print("Generating Selenium Scripts...")
        print("=" * 80)

        scripts = SeleniumGenerator.generate(
            request.test_cases,
            request.application_url
        )

        # ------------------------------------------
        # Remove Old Scripts
        # ------------------------------------------

        for file in GENERATED_TESTS_DIR.glob("test_*.py"):
            file.unlink()

        saved_files = []

        # ------------------------------------------
        # Save New Scripts
        # ------------------------------------------

        for script in scripts.scripts:

            filename = script.file_name.strip()

            if not filename.startswith("test_"):
                filename = f"test_{filename}"

            if not filename.endswith(".py"):
                filename += ".py"

            code = script.code

            # Remove Markdown Fences
            code = (
                code.replace("```python", "")
                    .replace("```", "")
                    .strip()
            )

            # Validate Python Syntax
            ast.parse(code)

            file_path = GENERATED_TESTS_DIR / filename

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(code)

            saved_files.append(filename)

            print(f"Saved: {file_path}")

        print("=" * 80)
        print("Selenium Generation Completed")
        print("=" * 80)

        return {

            "status": "SUCCESS",

            "message": "Selenium scripts generated successfully.",

            "files": saved_files,

            "scripts": scripts.model_dump()["scripts"]

        }

    except SyntaxError as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Generated Python contains syntax errors: {e}"
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )