from app.core.ai_client import ai_client
from app.core.prompt_loader import load_prompt

from app.schemas.requirement_schema import RequirementAnalysis
from app.schemas.testscenario_schema import (
    TestScenario,
    TestScenarioList
)


class TestScenarioGenerator:

    # -----------------------------------------------------
    # Remove Unsupported Scenarios
    # -----------------------------------------------------

    @staticmethod
    def filter_scenarios(
        scenarios: list[TestScenario]
    ) -> list[TestScenario]:

        unsupported = [
            "registration",
            "signup",
            "checkout",
            "payment",
            "shopping cart",
            "profile",
            "order",
            "invoice"
        ]

        filtered = []

        for scenario in scenarios:

            title = scenario.title.lower()

            skip = False

            for feature in unsupported:

                if feature in title:
                    skip = True
                    break

            if not skip:
                filtered.append(scenario)

        return filtered

    # -----------------------------------------------------
    # Remove Duplicate Scenarios
    # -----------------------------------------------------

    @staticmethod
    def remove_duplicates(
        scenarios: list[TestScenario]
    ) -> list[TestScenario]:

        unique = []
        seen = set()

        for scenario in scenarios:

            key = scenario.title.lower().strip()

            if key not in seen:

                seen.add(key)
                unique.append(scenario)

        return unique

    # -----------------------------------------------------
    # Generate Test Scenarios
    # -----------------------------------------------------

    @staticmethod
    def generate(
        analysis: RequirementAnalysis
    ) -> TestScenarioList:

        prompt = load_prompt(
            "scenario_prompt.txt"
        )

        prompt = prompt.replace(
            "{analysis}",
            analysis.model_dump_json(
                indent=2
            )
        )

        print("=" * 80)
        print("SCENARIO PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        result = ai_client.generate_structured(
            prompt,
            dict
        )

        print("=" * 80)
        print("RAW SCENARIO RESPONSE")
        print("=" * 80)
        print(result)
        print("=" * 80)

        if "test_scenarios" not in result:

            raise Exception(
                "LLM response does not contain 'test_scenarios'."
            )

        scenarios = []

        counter = 1

        # -------------------------------------------------
        # Response Already List
        # -------------------------------------------------

        if isinstance(
            result["test_scenarios"],
            list
        ):

            for item in result["test_scenarios"]:

                scenarios.append(

                    TestScenario(

                        id=item.get(
                            "id",
                            f"TS{counter:03}"
                        ),

                        title=item.get(
                            "title",
                            item.get(
                                "description",
                                "Untitled Scenario"
                            )
                        ),

                        category=item.get(
                            "category",
                            "Functional"
                        ),

                        priority=item.get(
                            "priority",
                            "High"
                        )

                    )

                )

                counter += 1

        # -------------------------------------------------
        # Categorized Response
        # -------------------------------------------------

        elif isinstance(
            result["test_scenarios"],
            dict
        ):

            for category, values in result[
                "test_scenarios"
            ].items():

                if not isinstance(values, list):
                    continue

                for item in values:

                    scenarios.append(

                        TestScenario(

                            id=f"TS{counter:03}",

                            title=item.get(
                                "title",
                                item.get(
                                    "description",
                                    "Untitled Scenario"
                                )
                            ),

                            category=category.capitalize(),

                            priority=item.get(
                                "priority",
                                "High"
                            )

                        )

                    )

                    counter += 1

        else:

            raise Exception(
                "Invalid format for test_scenarios."
            )

        # -------------------------------------------------
        # Remove Duplicates
        # -------------------------------------------------

        scenarios = (
            TestScenarioGenerator.remove_duplicates(
                scenarios
            )
        )

        # -------------------------------------------------
        # Remove Unsupported Scenarios
        # -------------------------------------------------

        scenarios = (
            TestScenarioGenerator.filter_scenarios(
                scenarios
            )
        )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        if len(scenarios) == 0:

            raise Exception(
                "No valid scenarios generated."
            )

        print("=" * 80)
        print("FINAL TEST SCENARIOS")
        print("=" * 80)

        for scenario in scenarios:

            print(
                scenario.model_dump()
            )

        print("=" * 80)

        return TestScenarioList(
            test_scenarios=scenarios
        )