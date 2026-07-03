from pydantic import BaseModel


class RequirementAnalysis(BaseModel):
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    edge_cases: list[str]
    risks: list[str]