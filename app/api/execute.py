from fastapi import APIRouter, HTTPException

from app.services.execution_service import ExecutionService
from app.services.healing_service import HealingService

router = APIRouter(
    tags=["Execution"]
)


@router.post("/execute")
async def execute_tests():
    """
    Execute all generated Selenium test scripts.
    """

    try:
        return ExecutionService.execute()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/heal")
async def heal_failed_tests():
    """
    Self-healing: repair the scripts that failed in the last
    run using their runtime errors, then re-run the suite.
    """

    try:
        return HealingService.heal_and_rerun()

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
