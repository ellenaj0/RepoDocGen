# RepoDocGen

An LLM-powered agent for generating comprehensive repository- and file-level documentation and question answering for codebases.

## Features

- 🔍 Repository-level and file-level code understanding and summarization
- 📝 Automatic documentation generation
- 💬 RAG-based Q&A chatbot 

## Quick Start

### Installation

#### Option 1: Using Conda (Recommended)

```bash
# Create conda environment
conda env create -f environment.yaml
conda activate repodocgen
```

#### Option 2: Using pip (Recommended)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
- Get OpenAI API key from: https://platform.openai.com/api-keys
- Get Voyage API key from: https://www.voyageai.com/ 

## Usage

### Basic Usage

```bash
# Generate documentation for a repository
python main.py /path/to/repo

# Generate and launch web interface
python main.py /path/to/repo --web

# Save vector index for later use
python main.py /path/to/repo --save-index --output ./my_output
```

### Programmatic Usage

```python
from src.parser.code_parser import CodeParser
from src.summarizer.summarizer import CodeSummarizer
from src.rag.vector_store import VectorStore
from src.rag.hybrid_search import HybridSearch
from src.chatbot.qa_bot import QABot

# Parse repository
parser = CodeParser()
analyses = parser.parse_repository("/path/to/repo")

# Generate summaries
summarizer = CodeSummarizer()
summaries = summarizer.summarize_repository(analyses)

# Build RAG index
vector_store = VectorStore()
hybrid_search = HybridSearch(vector_store)
# ... (see examples/quickstart.py for complete example)

# Query repository
qa_bot = QABot(hybrid_search)
result = qa_bot.query("Where is function X defined?")
print(result['answer'])
```

## Project Structure

```
RepoDocGen/
├── src/
│   ├── parser/          # Tree-sitter code parsing
│   ├── summarizer/      # Code summarization module
│   ├── rag/             # RAG and vector database
│   ├── chatbot/         # Q&A chatbot
│   └── web/             # Web interface
├── tests/               # Unit tests
├── examples/            # Quickstart example
├── main.py              # Main entry point
├── requirements.txt
├── environment.yaml
├── SETUP_GUIDE.md
└── README.md
```

## Team
- Aryaman Velampalli (fin1cky)
- Chengtao Dai (HeyyDario)
- Ellena Jiang (ellenaj0)

This project was done as a class project for COMS 6998-013 LLM Based Generative AI, Fall 2025 at Columbia University.
