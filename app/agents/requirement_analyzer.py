from app.core.ai_client import ai_client
from app.core.prompt_loader import load_prompt

from app.schemas.requirement_schema import RequirementAnalysis


class RequirementAnalyzer:

    @staticmethod
    def analyze(requirement: str) -> RequirementAnalysis:

        prompt = load_prompt("requirement_prompt.txt")

        prompt = prompt.replace(
            "{requirement}",
            requirement
        )

        return ai_client.generate_structured(
            prompt,
            RequirementAnalysis
        )