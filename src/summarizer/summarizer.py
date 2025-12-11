"""
Code summarization using OpenAI LLM
"""

from openai import OpenAI
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.config import Config
from src.parser.code_parser import FileAnalysis, CodeElement


@dataclass
class FileSummary:
    """Summary of a code file"""

    file_path: str
    language: str
    high_level_summary: str
    main_functionalities: List[str]
    key_elements: List[Dict[str, str]]  # [{name, type, description}]
    dependencies: List[str]


class CodeSummarizer:
    """Generate code summaries using OpenAI LLM"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenAI API"""
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model_name = model or Config.LLM_MODEL

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set. Please check your .env file.")

        self.client = OpenAI(api_key=self.api_key)

        # Generation config
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS

    def summarize_file(self, file_analysis: FileAnalysis) -> FileSummary:
        """Generate summary for a single file"""

        # Build context from parsed elements
        elements_context = self._build_elements_context(file_analysis.elements)

        # Create prompt
        prompt = f"""Analyze this {file_analysis.language} source code file and provide a structured summary.

File: {file_analysis.file_path}
Lines of code: {file_analysis.line_count}

Code Structure:
{elements_context}

Imports:
{chr(10).join(file_analysis.imports) if file_analysis.imports else 'None'}

Code Content:
{file_analysis.raw_content}  # First 3000 chars to stay within limits

Please provide:
1. High-level summary (2-3 sentences about what this file does)
2. Main functionalities (bullet points)
3. Key code elements with brief descriptions
4. External dependencies mentioned

Format your response as:
SUMMARY:
[your summary here]

FUNCTIONALITIES:
- [functionality 1]
- [functionality 2]

KEY ELEMENTS:
- [element_type] [name]: [description]

DEPENDENCIES:
- [dependency 1]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return self._parse_summary_response(
                response.choices[0].message.content,
                file_analysis.file_path,
                file_analysis.language,
            )
        except Exception as e:
            print(f"Error summarizing {file_analysis.file_path}: {e}")
            return self._create_fallback_summary(file_analysis)

    def _build_elements_context(self, elements: List[CodeElement]) -> str:
        """Build a string representation of code elements"""
        if not elements:
            return "No functions or classes detected"

        lines = []
        for elem in elements:
            parent = f" (in {elem.parent})" if elem.parent else ""
            lines.append(
                f"- {elem.type}: {elem.name}{parent} (lines {elem.start_line}-{elem.end_line})"
            )

        return "\n".join(lines)

    def _parse_summary_response(
        self, response_text: str, file_path: str, language: str
    ) -> FileSummary:
        """Parse LLM response into FileSummary object"""
        sections = {
            "SUMMARY:": "",
            "FUNCTIONALITIES:": [],
            "KEY ELEMENTS:": [],
            "DEPENDENCIES:": [],
        }

        current_section = None
        for line in response_text.split("\n"):
            line = line.strip()
            if line in sections:
                current_section = line
            elif current_section and line:
                if current_section == "SUMMARY:":
                    sections[current_section] += line + " "
                else:
                    # Remove bullet points and clean
                    cleaned = line.lstrip("- •*").strip()
                    if cleaned:
                        sections[current_section].append(cleaned)

        # Parse key elements
        key_elements = []
        for elem_str in sections["KEY ELEMENTS:"]:
            parts = elem_str.split(":", 1)
            if len(parts) == 2:
                name_type = parts[0].strip()
                description = parts[1].strip()
                key_elements.append(
                    {"name": name_type, "type": "element", "description": description}
                )

        return FileSummary(
            file_path=file_path,
            language=language,
            high_level_summary=sections["SUMMARY:"].strip(),
            main_functionalities=sections["FUNCTIONALITIES:"],
            key_elements=key_elements,
            dependencies=sections["DEPENDENCIES:"],
        )

    def _create_fallback_summary(self, file_analysis: FileAnalysis) -> FileSummary:
        """Create a basic summary if LLM fails"""
        return FileSummary(
            file_path=file_analysis.file_path,
            language=file_analysis.language,
            high_level_summary=f"A {file_analysis.language} file with {len(file_analysis.elements)} code elements.",
            main_functionalities=[
                f"Contains {len([e for e in file_analysis.elements if e.type == 'function'])} functions",
                f"Contains {len([e for e in file_analysis.elements if e.type == 'class'])} classes",
            ],
            key_elements=[
                {
                    "name": e.name,
                    "type": e.type,
                    "description": f"Defined at line {e.start_line}",
                }
                for e in file_analysis.elements[:5]
            ],
            dependencies=file_analysis.imports[:5],
        )

    def summarize_repository(
        self, file_analyses: List[FileAnalysis]
    ) -> List[FileSummary]:
        """Summarize all files in a repository"""
        summaries = []
        total = len(file_analyses)

        for i, analysis in enumerate(file_analyses, 1):
            print(f"Summarizing {i}/{total}: {analysis.file_path}")
            summary = self.summarize_file(analysis)
            summaries.append(summary)

        return summaries


def main():
    """Test the summarizer"""
    from src.parser.code_parser import CodeParser

    parser = CodeParser()
    summarizer = CodeSummarizer()

    # Parse current file
    analysis = parser.parse_file(__file__)

    if analysis:
        print("Generating summary...")
        summary = summarizer.summarize_file(analysis)

        print(f"\n=== Summary of {summary.file_path} ===")
        print(f"\nHigh-level: {summary.high_level_summary}")
        print("\nFunctionalities:")
        for func in summary.main_functionalities:
            print(f"  - {func}")


if __name__ == "__main__":
    main()
