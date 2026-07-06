"""Unit tests for pytest output parsing (history + self-healing)."""

from app.services.execution_service import (
    parse_pytest_summary,
    parse_failed_tests,
)


class TestParsers:

    def test_mixed_summary(self):
        out = "==== 2 failed, 3 passed, 1 skipped in 42.31s ===="
        counts = parse_pytest_summary(out)
        assert counts["failed"] == 2
        assert counts["passed"] == 3
        assert counts["skipped"] == 1

    def test_all_passed(self):
        counts = parse_pytest_summary("==== 4 passed in 12.00s ====")
        assert counts["passed"] == 4
        assert counts["failed"] == 0

    def test_failed_files_extracted_in_order(self):
        out = (
            "FAILED generated_tests/test_a.py::test_a - Timeout\n"
            "FAILED generated_tests/test_b.py::test_b - AssertionError\n"
            "FAILED generated_tests/test_a.py::test_a2 - Timeout\n"
        )
        files = parse_failed_tests(out)
        assert files == [
            "generated_tests/test_a.py",
            "generated_tests/test_b.py",
        ]

    def test_no_failures(self):
        assert parse_failed_tests("all good") == []
