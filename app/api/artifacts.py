import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    tags=["Artifacts"]
)

REPORTS = Path("reports")
GENERATED_TESTS = Path("generated_tests")
UPLOADS = Path("uploads")


@router.get("/report")
def get_report():
    """Serve the latest HTML test report."""

    report = REPORTS / "report.html"

    if not report.exists():
        raise HTTPException(
            status_code=404,
            detail="No report generated yet."
        )

    return FileResponse(report, media_type="text/html")


@router.get("/history")
def get_history():
    """Return the execution history as JSON."""

    history_file = REPORTS / "history.json"

    if not history_file.exists():
        return []

    try:
        return json.loads(history_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


@router.get("/artifacts/tests")
def list_generated_tests():
    """Return the generated Selenium scripts (name + code)."""

    if not GENERATED_TESTS.exists():
        return []

    return [
        {
            "name": path.name,
            "code": path.read_text(encoding="utf-8", errors="replace")
        }
        for path in sorted(GENERATED_TESTS.glob("test_*.py"))
    ]


@router.get("/artifacts/uploads")
def list_uploads():
    """Return uploaded requirement documents (name + text content)."""

    if not UPLOADS.exists():
        return []

    files = []

    for path in sorted(UPLOADS.iterdir()):
        if not path.is_file():
            continue
        files.append({
            "name": path.name,
            "content": path.read_text(encoding="utf-8", errors="replace")
        })

    return files
