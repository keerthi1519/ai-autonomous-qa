from fastapi import APIRouter, HTTPException

from app.services.execution_service import ExecutionService

router = APIRouter(
    tags=["Execution"]
)


@router.post("/execute")
async def execute_tests():
    """
    Execute all generated Selenium test scripts.
    """

    try:

        result = ExecutionService.execute()

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )