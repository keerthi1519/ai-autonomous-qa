"""Unit tests for the pydantic API schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.requirement_schema import RequirementAnalysis
from app.schemas.testcase_schema import TestCase as QATestCase
from app.schemas.testcase_schema import TestCaseList
from app.schemas.selenium_schema import SeleniumScriptList


class TestSchemas:

    def test_requirement_analysis_valid(self):
        model = RequirementAnalysis(
            functional_requirements=["login"],
            non_functional_requirements=["fast"],
            edge_cases=["empty password"],
            risks=["credential leak"],
        )
        assert model.functional_requirements == ["login"]

    def test_requirement_analysis_missing_field(self):
        with pytest.raises(ValidationError):
            RequirementAnalysis(functional_requirements=["login"])

    def test_testcase_roundtrip(self):
        case = QATestCase(
            test_case_id="TC001",
            title="Valid login",
            scenario="TS001",
            priority="High",
            test_type="Functional",
            preconditions=["user exists"],
            steps=["open page", "enter creds", "submit"],
            expected_result="dashboard shown",
        )
        dumped = TestCaseList(test_cases=[case]).model_dump()
        assert dumped["test_cases"][0]["test_case_id"] == "TC001"

    def test_selenium_script_list_rejects_missing_code(self):
        with pytest.raises(ValidationError):
            SeleniumScriptList.model_validate(
                {"scripts": [{"test_case_id": "TC1", "file_name": "x.py"}]}
            )
