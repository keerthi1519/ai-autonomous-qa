import re
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.requirement_service import RequirementService
from app.agents.requirement_analyzer import RequirementAnalyzer

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _safe_filename(original_name: str) -> str:
    """
    Build a safe filename from a user-supplied one.

    - Strips any directory components (defeats path traversal
      like '../generated_tests/test_evil.py').
    - Whitelists the extension.
    - Removes unsafe characters and prefixes a UUID to
      avoid collisions/overwrites.
    """

    if not original_name:
        raise HTTPException(
            status_code=400,
            detail="Missing filename."
        )

    # Drop any path components (handles both / and \)
    name = Path(original_name.replace("\\", "/")).name

    extension = Path(name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{extension}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        )

    stem = re.sub(r"[^A-Za-z0-9_-]", "_", Path(name).stem)[:100]

    return f"{uuid.uuid4().hex[:8]}_{stem}{extension}"


@router.post("/upload")
async def upload_requirement(
    file: UploadFile = File(...),
    application_url: str = Form(...)
):
    """
    Upload requirement document,
    analyze requirement,
    and store the application URL.
    """

    filename = _safe_filename(file.filename)

    file_path = (UPLOAD_DIR / filename).resolve()

    # Defense in depth: final path must stay inside uploads/
    if UPLOAD_DIR.resolve() not in file_path.parents:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    requirement_text = RequirementService.extract_text(
        str(file_path)
    )

    # Analyze requirement
    analysis = RequirementAnalyzer.analyze(
        requirement_text
    )

    return {
        "status": "success",
        "application_url": application_url,
        "analysis": analysis
    }
