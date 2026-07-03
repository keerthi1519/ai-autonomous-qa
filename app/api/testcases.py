from fastapi import APIRouter, HTTPException
import traceback

from app.schemas.testscenario_schema import TestScenarioList
from app.schemas.testcase_schema import TestCaseList

from app.agents.testcase_generator import TestCaseGenerator

router = APIRouter()


@router.post(
    "/generate-testcases",
    response_model=TestCaseList
)
async def generate_testcases(
    scenarios: TestScenarioList
):

    try:

        return TestCaseGenerator.generate(
            scenarios
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )