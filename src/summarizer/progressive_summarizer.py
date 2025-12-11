"""
Progressive summarization for large repositories
Maintains cumulative summaries while processing files to handle context window limits
"""

from openai import OpenAI
from typing import List, Dict
from dataclasses import dataclass

from src.config import Config
from src.summarizer.summarizer import FileSummary


@dataclass
class RepositorySummary:
    """High-level summary of entire repository"""

    repo_name: str
    total_files: int
    languages: Dict[str, int]  # {language: file_count}
    architecture_summary: str
    main_modules: List[str]
    key_functionalities: List[str]
    entry_points: List[str]


class ProgressiveSummarizer:
    """
    Progressively summarize large repositories by maintaining
    cumulative summaries at different granularities
    """

    def __init__(self, api_key: str = None, model: str = None):
        """Initialize with OpenAI API"""
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model_name = model or Config.LLM_MODEL

        self.client = OpenAI(api_key=self.api_key)

        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS

    def create_repository_summary(
        self, file_summaries: List[FileSummary], repo_name: str = "Unknown"
    ) -> RepositorySummary:
        """Create high-level repository summary from file summaries"""

        # Aggregate basic statistics
        languages = {}
        all_functionalities = []

        for summary in file_summaries:
            languages[summary.language] = languages.get(summary.language, 0) + 1
            all_functionalities.extend(summary.main_functionalities)

        # Group summaries by directory/module
        modules = self._group_by_module(file_summaries)

        # Create prompt for LLM to synthesize high-level summary
        prompt = self._build_repo_summary_prompt(
            file_summaries, modules, languages, repo_name
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return self._parse_repo_summary(
                response.choices[0].message.content,
                repo_name,
                len(file_summaries),
                languages,
            )
        except Exception as e:
            print(f"Error creating repository summary: {e}")
            return self._create_fallback_repo_summary(
                repo_name, len(file_summaries), languages
            )

    def _group_by_module(
        self, file_summaries: List[FileSummary]
    ) -> Dict[str, List[FileSummary]]:
        """Group files by their directory/module"""
        modules = {}
        for summary in file_summaries:
            # Extract module name from path (first directory after src/)
            parts = summary.file_path.split("/")
            if "src" in parts:
                idx = parts.index("src")
                module = parts[idx + 1] if idx + 1 < len(parts) else "root"
            else:
                module = parts[0] if parts else "root"

            if module not in modules:
                modules[module] = []
            modules[module].append(summary)

        return modules

    def _build_repo_summary_prompt(
        self,
        file_summaries: List[FileSummary],
        modules: Dict[str, List[FileSummary]],
        languages: Dict[str, int],
        repo_name: str,
    ) -> str:
        """Build prompt for repository-level summarization"""

        # Sample representative files
        sample_summaries = file_summaries#[:10]  # Take first 10 as representatives

        files_context = "\n\n".join(
            [
                f"File: {s.file_path}\nSummary: {s.high_level_summary}\nFunctionalities: {', '.join(s.main_functionalities[:5])}"
                for s in sample_summaries
            ]
        )

        modules_list = "\n".join(
            [f"- {name}: {len(files)} files" for name, files in modules.items()]
        )

        return f"""Analyze this code repository and provide a high-level architectural summary.

Repository: {repo_name}
Total Files: {len(file_summaries)}
Languages: {', '.join([f'{lang} ({count} files)' for lang, count in languages.items()])}

Modules/Directories:
{modules_list}

Sample File Summaries:
{files_context}

Please provide:
1. ARCHITECTURE: High-level architecture summary (2-3 sentences about overall structure and design)
2. MAIN_MODULES: List the main modules/components and their purposes
3. KEY_FUNCTIONALITIES: Core functionalities this repository implements
4. ENTRY_POINTS: Likely entry points or main files (e.g., main.py, __main__.py, app.py)

Format:
ARCHITECTURE:
[your summary]

MAIN_MODULES:
- [module]: [purpose]

KEY_FUNCTIONALITIES:
- [functionality]

ENTRY_POINTS:
- [file]: [purpose]
"""

    def _parse_repo_summary(
        self,
        response_text: str,
        repo_name: str,
        total_files: int,
        languages: Dict[str, int],
    ) -> RepositorySummary:
        """Parse LLM response into RepositorySummary"""
        sections = {
            "ARCHITECTURE:": "",
            "MAIN_MODULES:": [],
            "KEY_FUNCTIONALITIES:": [],
            "ENTRY_POINTS:": [],
        }

        current_section = None
        for line in response_text.split("\n"):
            line = line.strip()
            if line in sections:
                current_section = line
            elif current_section and line:
                if current_section == "ARCHITECTURE:":
                    sections[current_section] += line + " "
                else:
                    cleaned = line.lstrip("- •*").strip()
                    if cleaned:
                        sections[current_section].append(cleaned)

        return RepositorySummary(
            repo_name=repo_name,
            total_files=total_files,
            languages=languages,
            architecture_summary=sections["ARCHITECTURE:"].strip(),
            main_modules=sections["MAIN_MODULES:"],
            key_functionalities=sections["KEY_FUNCTIONALITIES:"],
            entry_points=sections["ENTRY_POINTS:"],
        )

    def _create_fallback_repo_summary(
        self, repo_name: str, total_files: int, languages: Dict[str, int]
    ) -> RepositorySummary:
        """Create basic summary if LLM fails"""
        return RepositorySummary(
            repo_name=repo_name,
            total_files=total_files,
            languages=languages,
            architecture_summary=f"A {', '.join(languages.keys())} repository with {total_files} files.",
            main_modules=["Unable to determine modules"],
            key_functionalities=["Code organization", "Implementation logic"],
            entry_points=["Unknown - manual inspection required"],
        )
