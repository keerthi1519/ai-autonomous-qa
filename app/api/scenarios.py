from fastapi import APIRouter, HTTPException
import traceback

from app.schemas.requirement_schema import RequirementAnalysis
from app.agents.test_scenario_generator import TestScenarioGenerator

router = APIRouter()


@router.post("/generate-scenarios")
async def generate_scenarios(
    analysis: RequirementAnalysis
):
    """
    Generate test scenarios from requirement analysis.
    """

    try:
        scenarios = TestScenarioGenerator.generate(analysis)
        return scenarios

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR IN /generate-scenarios")
        traceback.print_exc()
        print("=" * 60 + "\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )