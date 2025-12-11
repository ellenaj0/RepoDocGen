"""
Quick Start Example for RepoDocGen

This script demonstrates basic usage of RepoDocGen components.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.parser.code_parser import CodeParser
from src.summarizer.summarizer import CodeSummarizer
from src.rag.vector_store import VectorStore, Document
from src.rag.hybrid_search import HybridSearch
from src.chatbot.qa_bot import QABot


def main():
    print("=" * 60)
    print("RepoDocGen Quick Start Example")
    print("=" * 60)

    # Example 1: Parse a file
    print("\n1. Parsing a Python file")
    print("-" * 60)

    parser = CodeParser()
    current_file = __file__
    analysis = parser.parse_file(current_file)

    if analysis:
        print(f"File: {analysis.file_path}")
        print(f"Language: {analysis.language}")
        print(f"Elements found: {len(analysis.elements)}")
        for elem in analysis.elements[:3]:  # Show first 3
            print(f"  - {elem.type}: {elem.name} (line {elem.start_line})")

    # Example 2: Generate summary (requires API key)
    print("\n2. Generating code summary")
    print("-" * 60)
    print("Note: This requires OPENAI_API_KEY in .env file")

    try:
        summarizer = CodeSummarizer()
        summary = summarizer.summarize_file(analysis)
        print(f"Summary: {summary.high_level_summary[:150]}...")
    except Exception as e:
        print(f"Skipping summary generation: {e}")

    # Example 3: Build RAG index
    print("\n3. Building RAG index")
    print("-" * 60)

    # Create sample documents
    documents = [
        Document(
            id="1",
            content="def calculate_sum(a, b): return a + b",
            metadata={"file": "math.py", "type": "function"},
        ),
        Document(
            id="2",
            content="class UserManager: handles user authentication",
            metadata={"file": "auth.py", "type": "class"},
        ),
        Document(
            id="3",
            content="import numpy as np for numerical computations",
            metadata={"file": "data.py", "type": "import"},
        ),
    ]

    vector_store = VectorStore()
    hybrid_search = HybridSearch(vector_store)
    hybrid_search.index_documents(documents)

    print(f"Indexed {len(documents)} documents")

    # Example 4: Query with QA bot
    print("\n4. Querying the repository")
    print("-" * 60)

    try:
        qa_bot = QABot(hybrid_search)

        questions = [
            "What does calculate_sum do?",
            "How do I manage users?",
        ]

        for q in questions:
            print(f"\nQ: {q}")
            result = qa_bot.query(q)
            print(f"A: {result['answer'][:150]}...")

    except Exception as e:
        print(f"QA bot requires API key: {e}")

    print("\n" + "=" * 60)
    print("Quick start complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
