"""
Language-specific configurations for Tree-sitter parsing
"""

LANGUAGE_CONFIGS = {
    "python": {
        "function_types": ["function_definition"],
        "class_types": ["class_definition"],
        "import_types": ["import_statement", "import_from_statement"],
        "comment_types": ["comment"],
    },
}
