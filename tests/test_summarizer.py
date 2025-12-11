"""
Tests for summarization module
"""

import pytest
from unittest.mock import Mock, patch
from src.summarizer.summarizer import CodeSummarizer, FileSummary
from src.parser.code_parser import FileAnalysis, CodeElement

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestCodeSummarizer:
    """Test suite for CodeSummarizer"""

    @pytest.fixture
    def mock_file_analysis(self):
        """Create mock FileAnalysis"""
        elements = [
            CodeElement(
                type="function",
                name="calculate_sum",
                start_line=1,
                end_line=3,
                body="def calculate_sum(a, b):\n    return a + b",
            )
        ]

        return FileAnalysis(
            file_path="test.py",
            language="python",
            elements=elements,
            imports=["import numpy as np"],
            dependencies=[],
            raw_content="def calculate_sum(a, b):\n    return a + b",
            line_count=2,
        )

    def test_create_fallback_summary(self, mock_file_analysis):
        """Test fallback summary creation"""
        # Skip API key requirement for this test
        with patch("src.config.Config.OPENAI_API_KEY", "test_key"):
            summarizer = CodeSummarizer()
            summary = summarizer._create_fallback_summary(mock_file_analysis)

            assert isinstance(summary, FileSummary)
            assert summary.file_path == "test.py"
            assert summary.language == "python"
            assert len(summary.main_functionalities) > 0
