from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.scenarios import router as scenario_router
from app.api.testcases import router as testcase_router
from app.api.selenium import router as selenium_router
from app.api.execute import router as execute_router
from app.api.artifacts import router as artifacts_router

app = FastAPI(title="AI Autonomous QA Engineer")

# Routers in pipeline order:
# upload -> scenarios -> test cases -> selenium scripts -> execute
app.include_router(upload_router)
app.include_router(scenario_router)
app.include_router(testcase_router)
app.include_router(selenium_router)
app.include_router(execute_router)
app.include_router(artifacts_router)


@app.get("/")
def root():
    return {
        "message": "AI Autonomous QA Engineer Running"
    }
