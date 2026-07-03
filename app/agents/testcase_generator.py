import json

from app.core.ai_client import ai_client
from app.core.prompt_loader import load_prompt

from app.schemas.testscenario_schema import TestScenarioList
from app.schemas.testcase_schema import TestCaseList


class TestCaseGenerator:

    @staticmethod
    def generate(
        scenarios: TestScenarioList
    ) -> TestCaseList:

        prompt = load_prompt("generate_test_cases.txt")

        prompt = prompt.replace(
            "{scenarios}",
            json.dumps(
                scenarios.model_dump(),
                indent=2
            )
        )

        raw = ai_client.generate_structured(
            prompt,
            dict
        )

        print("=" * 60)
        print("RAW TEST CASE RESPONSE")
        print(json.dumps(raw, indent=2))
        print("=" * 60)

        # -----------------------------
        # Normalize top-level response
        # -----------------------------
        if "test_cases" in raw:
            normalized = raw

        elif "cases" in raw:
            normalized = {
                "test_cases": raw["cases"]
            }

        elif isinstance(raw, list):
            normalized = {
                "test_cases": raw
            }

        else:
            raise Exception(
                "Unexpected AI response format."
            )

        # -----------------------------
        # Normalize each test case
        # -----------------------------
        for tc in normalized["test_cases"]:

            # Preconditions
            if isinstance(tc.get("preconditions"), str):
                tc["preconditions"] = [
                    tc["preconditions"]
                ]

            elif tc.get("preconditions") is None:
                tc["preconditions"] = []

            # Steps
            if isinstance(tc.get("steps"), str):
                tc["steps"] = [
                    tc["steps"]
                ]

            elif tc.get("steps") is None:
                tc["steps"] = []

            # Expected Result
            if tc.get("expected_result") is None:
                tc["expected_result"] = ""

            # Priority
            if tc.get("priority") is None:
                tc["priority"] = "Medium"

            # Test Type
            if tc.get("test_type") is None:
                tc["test_type"] = "Functional"

            # Scenario
            if tc.get("scenario") is None:
                tc["scenario"] = ""

        print("=" * 60)
        print("NORMALIZED TEST CASES")
        print(json.dumps(normalized, indent=2))
        print("=" * 60)

        return TestCaseList.model_validate(
            normalized
        )