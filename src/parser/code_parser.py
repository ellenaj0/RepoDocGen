"""
Tree-sitter based code parser for Python
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

from src.parser.language_configs import LANGUAGE_CONFIGS


@dataclass
class CodeElement:
    """Represents a parsed code element"""

    type: str  # function, class, method, variable
    name: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    body: Optional[str] = None
    parent: Optional[str] = None  # For methods inside classes


@dataclass
class FileAnalysis:
    """Analysis result for a single file"""

    file_path: str
    language: str
    elements: List[CodeElement]
    imports: List[str]
    dependencies: List[str]  # Cross-file dependencies
    raw_content: str
    line_count: int


class CodeParser:
    """Python code parser using Tree-sitter"""

    def __init__(self):
        """Initialize Python parser"""
        self.parsers = {}
        self._init_parsers()

    def _init_parsers(self):
        """Initialize Tree-sitter parser for Python"""
        try:
            language = Language(tspython.language())
            parser = Parser(language)
            self.parsers["python"] = {
                "parser": parser,
                "language": language,
            }
            print("✓ Initialized Python parser")
        except Exception as e:
            print(f"✗ Failed to initialize Python parser: {e}")

    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect if file is a Python file from file extension"""
        ext = Path(file_path).suffix.lower()
        if ext == ".py":
            return "python"
        return None

    def parse_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Parse a single source code file"""
        try:
            # Detect language
            language = self.detect_language(file_path)
            if not language or language not in self.parsers:
                return None

            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse with Tree-sitter
            parser_info = self.parsers[language]
            tree = parser_info["parser"].parse(bytes(content, "utf8"))

            # Extract code elements
            elements = self._extract_elements(tree.root_node, content, language)
            imports = self._extract_imports(tree.root_node, content, language)

            return FileAnalysis(
                file_path=file_path,
                language=language,
                elements=elements,
                imports=imports,
                dependencies=[],  # Will be populated later by dependency analyzer
                raw_content=content,
                line_count=len(content.splitlines()),
            )

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _extract_elements(
        self, root: Node, content: str, language: str
    ) -> List[CodeElement]:
        """Extract functions, classes, methods from AST"""
        elements = []
        config = LANGUAGE_CONFIGS.get(language, {})

        def traverse(node: Node, parent_class: Optional[str] = None):
            # Check if this node is a code element we care about
            element = self._create_element(node, content, language, parent_class)
            if element:
                elements.append(element)
                # If it's a class, traverse its children with this class as parent
                if element.type == "class":
                    for child in node.children:
                        traverse(child, parent_class=element.name)
            else:
                # Continue traversing
                for child in node.children:
                    traverse(child, parent_class)

        traverse(root)
        return elements

    def _create_element(
        self, node: Node, content: str, language: str, parent_class: Optional[str]
    ) -> Optional[CodeElement]:
        """Create CodeElement from AST node"""
        config = LANGUAGE_CONFIGS.get(language, {})

        # Determine element type
        element_type = None
        if node.type in config.get("function_types", []):
            element_type = "function" if not parent_class else "method"
        elif node.type in config.get("class_types", []):
            element_type = "class"

        if not element_type:
            return None

        # Extract name
        name = self._extract_name(node, language)
        if not name:
            return None

        # Extract other details
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        body = content[node.start_byte : node.end_byte]

        return CodeElement(
            type=element_type,
            name=name,
            start_line=start_line,
            end_line=end_line,
            body=body,
            parent=parent_class,
        )

    def _extract_name(self, node: Node, language: str) -> Optional[str]:
        """Extract name from function/class node"""
        # Look for 'name' or 'identifier' child
        for child in node.children:
            if child.type in ["identifier", "name"]:
                return child.text.decode("utf8")
        return None

    def _extract_imports(self, root: Node, content: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        config = LANGUAGE_CONFIGS.get(language, {})
        import_types = config.get("import_types", [])

        def traverse(node: Node):
            if node.type in import_types:
                import_text = content[node.start_byte : node.end_byte]
                imports.append(import_text)
            for child in node.children:
                traverse(child)

        traverse(root)
        return imports

    def parse_repository(
        self, repo_path: str, exclude_patterns: Optional[List[str]] = None
    ) -> List[FileAnalysis]:
        """Parse all Python files in a repository"""
        if exclude_patterns is None:
            exclude_patterns = ["node_modules", "venv", ".git", "__pycache__"]

        results = []
        repo_path = Path(repo_path)

        for file_path in repo_path.rglob("*"):
            # Skip if matches exclude pattern
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            # Skip if not a file
            if not file_path.is_file():
                continue

            # Try to parse
            analysis = self.parse_file(str(file_path))
            if analysis:
                results.append(analysis)

        print(f"Parsed {len(results)} files from {repo_path}")
        return results


def main():
    """Test the parser"""
    parser = CodeParser()

    # Test on current file
    current_file = __file__
    result = parser.parse_file(current_file)

    if result:
        print(f"\n=== Analysis of {result.file_path} ===")
        print(f"Language: {result.language}")
        print(f"Lines: {result.line_count}")
        print(f"\nFound {len(result.elements)} code elements:")
        for elem in result.elements:
            print(
                f"  - {elem.type.upper()}: {elem.name} (lines {elem.start_line}-{elem.end_line})"
            )


if __name__ == "__main__":
    main()
