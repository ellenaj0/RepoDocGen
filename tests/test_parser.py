"""
Tests for code parser module
"""

import pytest
from pathlib import Path
from src.parser.code_parser import CodeParser

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestCodeParser:
    """Test suite for CodeParser"""

    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return CodeParser()

    def test_parser_initialization(self, parser):
        """Test parser initializes correctly"""
        assert parser is not None
        assert "python" in parser.parsers

    def test_detect_language(self, parser):
        """Test language detection"""
        assert parser.detect_language("test.py") == "python"
        assert parser.detect_language("test.js") is None
        assert parser.detect_language("test.txt") is None

    def test_parse_python_file(self, parser, tmp_path):
        """Test parsing a simple Python file"""
        # Create temp Python file
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
        )

        result = parser.parse_file(str(test_file))

        assert result is not None
        assert result.language == "python"
        assert len(result.elements) >= 2  # function and class
        assert any(e.name == "add" for e in result.elements)
        assert any(e.name == "Calculator" for e in result.elements)

    def test_parse_invalid_file(self, parser):
        """Test parsing non-existent file"""
        result = parser.parse_file("nonexistent.py")
        assert result is None

    def test_parse_repository(self, parser, tmp_path):
        """Test parsing entire repository"""
        # Create temp repo structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass")
        (tmp_path / "src" / "utils.py").write_text("def util(): pass")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test(): pass")

        results = parser.parse_repository(str(tmp_path))

        assert len(results) == 3
        assert all(r.language == "python" for r in results)
