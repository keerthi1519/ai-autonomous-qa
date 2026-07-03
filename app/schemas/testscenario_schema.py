from pydantic import BaseModel


class TestScenario(BaseModel):
    id: str
    title: str
    category: str
    priority: str


class TestScenarioList(BaseModel):
    test_scenarios: list[TestScenario]