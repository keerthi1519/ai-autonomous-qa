from app.agents.requirement_analyzer import RequirementAnalyzer
from app.agents.test_scenario_generator import TestScenarioGenerator
from app.agents.testcase_generator import TestCaseGenerator
from app.agents.selenium_generator import SeleniumGenerator

from app.services.selenium_service import SeleniumService


class QAPipeline:

    @staticmethod
    def execute(requirement: str):

        print("\n========== STEP 1 ==========")
        analysis = RequirementAnalyzer.analyze(requirement)
        print("✅ Requirement analysis completed")

        print("\n========== STEP 2 ==========")
        scenarios = TestScenarioGenerator.generate(analysis)
        print("✅ Scenario generation completed")

        print("\n========== STEP 3 ==========")
        test_cases = TestCaseGenerator.generate(scenarios)
        print("✅ Test case generation completed")

        print("\n========== STEP 4 ==========")
        selenium_suite = SeleniumGenerator.generate(test_cases)
        print("✅ Selenium generation completed")

        print("\n========== STEP 5 ==========")
        SeleniumService.save(selenium_suite)
        print("✅ Selenium files saved")

        print("\n========== PIPELINE FINISHED ==========")

        return {
            "analysis": analysis,
            "scenarios": scenarios,
            "test_cases": test_cases,
            "selenium": selenium_suite
        }