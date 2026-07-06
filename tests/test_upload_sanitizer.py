"""Unit tests for the upload filename sanitizer (path-traversal defense)."""

import pytest
from fastapi import HTTPException

from app.api.upload import _safe_filename


class TestSafeFilename:

    def test_normal_pdf(self):
        result = _safe_filename("requirements.pdf")
        assert result.endswith(".pdf")
        assert "requirements" in result

    def test_path_traversal_is_stripped(self):
        result = _safe_filename("../generated_tests/test_evil.txt")
        assert "/" not in result
        assert ".." not in result
        assert result.endswith(".txt")

    def test_windows_path_traversal_is_stripped(self):
        result = _safe_filename("..\\app\\main.txt")
        assert "\\" not in result
        assert ".." not in result

    def test_python_file_rejected(self):
        with pytest.raises(HTTPException) as exc:
            _safe_filename("../generated_tests/test_evil.py")
        assert exc.value.status_code == 400

    def test_executable_rejected(self):
        with pytest.raises(HTTPException):
            _safe_filename("malware.exe")

    def test_empty_filename_rejected(self):
        with pytest.raises(HTTPException):
            _safe_filename("")

    def test_unsafe_characters_replaced(self):
        result = _safe_filename("my file (final)!.txt")
        stem = result.rsplit(".", 1)[0]
        # after the uuid prefix, only safe characters remain
        assert all(c.isalnum() or c in "_-" for c in stem)

    def test_unique_names_for_same_input(self):
        a = _safe_filename("report.docx")
        b = _safe_filename("report.docx")
        assert a != b
