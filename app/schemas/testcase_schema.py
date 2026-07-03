from typing import List
from pydantic import BaseModel


class TestCase(BaseModel):
    test_case_id: str
    title: str
    scenario: str
    priority: str
    test_type: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str


class TestCaseList(BaseModel):
    test_cases: List[TestCase]