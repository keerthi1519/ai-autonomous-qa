from pydantic import BaseModel

from app.schemas.testcase_schema import TestCaseList


class SeleniumRequest(BaseModel):
    application_url: str
    test_cases: TestCaseList