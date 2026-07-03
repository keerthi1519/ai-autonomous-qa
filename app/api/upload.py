import os
import shutil

from fastapi import APIRouter, UploadFile, File, Form

from app.services.requirement_service import RequirementService
from app.agents.requirement_analyzer import RequirementAnalyzer

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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

    # Save uploaded file
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    requirement_text = RequirementService.extract_text(
        file_path
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