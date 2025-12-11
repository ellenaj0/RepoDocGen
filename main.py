#!/usr/bin/env python3
"""
RepoDocGen - Main entry point
Generate comprehensive documentation for code repositories using LLMs
"""

import argparse
from pathlib import Path
import sys

from src.config import Config
from src.parser.code_parser import CodeParser
from src.summarizer.summarizer import CodeSummarizer
from src.summarizer.progressive_summarizer import ProgressiveSummarizer
from src.rag.vector_store import VectorStore, Document
from src.rag.hybrid_search import HybridSearch
from src.chatbot.qa_bot import QABot
from src.web.app import create_app


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="RepoDocGen: LLM-powered repository documentation generator"
    )

    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to repository or GitHub URL",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./output",
        help="Output directory for documentation (default: ./output)",
    )

    parser.add_argument(
        "--web",
        "-w",
        action="store_true",
        help="Launch web interface after generation",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=5000,
        help="Port for web interface (default: 5000)",
    )

    parser.add_argument(
        "--save-index",
        "-s",
        action="store_true",
        help="Save vector index to disk for later use",
    )

    return parser.parse_args()


def main():
    """Main execution flow"""
    args = parse_args()

    # Print configuration
    print("\n" + "=" * 60)
    print("RepoDocGen - Repository Documentation Generator")
    print("=" * 60 + "\n")
    Config.print_config()

    # Validate configuration
    errors = Config.validate()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        print(f"\n❌ Error: Repository path '{repo_path}' does not exist")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📂 Processing repository: {repo_path}")
    print(f"📝 Output directory: {output_dir}\n")

    # Step 1: Parse repository
    print("=" * 60)
    print("STEP 1: Parsing Repository")
    print("=" * 60)
    parser = CodeParser()
    file_analyses = parser.parse_repository(
        str(repo_path), exclude_patterns=Config.EXCLUDE_PATTERNS
    )

    if not file_analyses:
        print("❌ No supported files found in repository")
        sys.exit(1)

    print(f"✓ Parsed {len(file_analyses)} files")

    # Step 2: Generate summaries
    print("\n" + "=" * 60)
    print("STEP 2: Generating File Summaries")
    print("=" * 60)
    summarizer = CodeSummarizer()
    file_summaries = summarizer.summarize_repository(file_analyses)
    print(f"✓ Generated {len(file_summaries)} file summaries")

    # Step 3: Generate repository-level summary
    print("\n" + "=" * 60)
    print("STEP 3: Generating Repository Summary")
    print("=" * 60)
    progressive_summarizer = ProgressiveSummarizer()
    repo_summary = progressive_summarizer.create_repository_summary(
        file_summaries, repo_name=repo_path.name
    )
    print("✓ Generated repository summary")
    print(f"\nArchitecture: {repo_summary.architecture_summary}")

    # Step 4: Build RAG index
    print("\n" + "=" * 60)
    print("STEP 4: Building RAG Index")
    print("=" * 60)

    # Create documents at multiple granularity levels
    documents = []

    # Track statistics
    file_doc_count = 0
    code_element_count = 0

    for i, (analysis, summary) in enumerate(zip(file_analyses, file_summaries)):
        # Level 1: File-level summary document
        file_doc = Document(
            id=f"file_{i}",
            content=f"{summary.high_level_summary}\n\nFunctionalities:\n"
            + "\n".join(f"- {f}" for f in summary.main_functionalities),
            metadata={
                "file_path": summary.file_path,
                "language": summary.language,
                "element_type": "file_summary",
            },
        )
        documents.append(file_doc)
        file_doc_count += 1

        # Level 2: Function/Class-level documents from parsed code
        for j, element in enumerate(analysis.elements):
            # Build document content with code details
            content_parts = []

            # Add header with element type and name
            header = f"{element.type.upper()}: {element.name}"
            if element.parent:
                header += f" (in class {element.parent})"
            content_parts.append(header)

            # Add file location
            content_parts.append(f"File: {summary.file_path}")
            content_parts.append(f"Lines: {element.start_line}-{element.end_line}")

            # Add signature if available
            if element.signature:
                content_parts.append(f"Signature: {element.signature}")

            # Add docstring if available
            if element.docstring:
                content_parts.append(f"Documentation: {element.docstring}")

            # Add code body (truncate if very long)
            if element.body:
                code = element.body
                if len(code) > 1500:  # Truncate very long functions
                    code = code[:1500] + "\n... (truncated)"
                content_parts.append(f"\nCode:\n{code}")

            code_doc = Document(
                id=f"file_{i}_code_{j}",
                content="\n".join(content_parts),
                metadata={
                    "file_path": summary.file_path,
                    "language": summary.language,
                    "element_type": element.type,
                    "element_name": element.name,
                    "line_range": f"{element.start_line}-{element.end_line}",
                    "parent": element.parent,
                },
            )
            documents.append(code_doc)
            code_element_count += 1

    # Build index
    vector_store = VectorStore()
    hybrid_search = HybridSearch(vector_store)
    hybrid_search.index_documents(documents)
    print(f"✓ Indexed {len(documents)} documents:")
    print(f"  - {file_doc_count} file-level summaries")
    print(f"  - {code_element_count} code elements (functions/classes/methods)")

    # Save index if requested
    if args.save_index:
        index_dir = output_dir / "index"
        index_dir.mkdir(exist_ok=True)
        vector_store.save(str(index_dir))

    # Step 5: Initialize QA Bot
    print("\n" + "=" * 60)
    print("STEP 5: Initializing QA Bot")
    print("=" * 60)
    qa_bot = QABot(hybrid_search)
    print("✓ QA Bot ready")

    # Test query
    test_query = "What are the main components of this repository?"
    print(f"\nTest Query: {test_query}")
    result = qa_bot.query(test_query)
    print(f"Answer: {result['answer'][:200]}...")

    # Step 6: Launch web interface (optional)
    if args.web:
        print("\n" + "=" * 60)
        print("STEP 6: Launching Web Interface")
        print("=" * 60)
        print(f"🌐 Starting server on http://localhost:{args.port}")
        print("Press Ctrl+C to stop\n")

        app = create_app(qa_bot, repo_summary, file_summaries)
        app.run(host="0.0.0.0", port=args.port, debug=False)
    else:
        print("\n" + "=" * 60)
        print("✅ Documentation Generation Complete!")
        print("=" * 60)
        print("\nTo launch web interface, run:")
        print(f"  python main.py {repo_path} --web\n")


if __name__ == "__main__":
    main()
