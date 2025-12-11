# RepoDocGen Setup Guide

## Project Structure

```
RepoDocGen/
├── src/                          # Main source code
│   ├── parser/                   # Tree-sitter code parsing
│   │   ├── code_parser.py        # Multi-language parser
│   │   └── language_configs.py   # Language-specific configs
│   ├── summarizer/               # Code summarization
│   │   ├── summarizer.py         # File-level summarization
│   │   └── progressive_summarizer.py  # Repository-level
│   ├── rag/                      # RAG and retrieval
│   │   ├── vector_store.py       # FAISS vector database
│   │   └── hybrid_search.py      # BM25 + semantic search
│   ├── chatbot/                  # Q&A chatbot
│   │   └── qa_bot.py             # RAG-based QA
│   ├── web/                      # Web interface
│   │   ├── app.py                # Flask application
│   │   └── templates/index.html  # Documentation UI
│   └── config.py                 # Central configuration
├── tests/                        # Unit tests
│   ├── test_parser.py
│   ├── test_summarizer.py
│   └── test_vector_store.py
├── examples/                     # Usage examples
│   └── quickstart.py
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
├── environment.yaml              # Conda environment
├── .env.example                  # Environment variables template
├── setup.py                      # Package setup
└── README.md                     # Project README
```

## Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project
cd <PATH_TO_REPODOCGEN>

# Option A: Using conda (recommended)
conda env create -f environment.yaml
conda activate repodocgen

# Option B: Using pip
python -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required:
#   OPENAI_API_KEY=your_openai_api_key_here
#   VOYAGE_API_KEY=your_voyage_api_key_here
```

Get your OpenAI API key from: https://platform.openai.com/api-keys
Get your Voyage API key from: https://www.voyageai.com/

### 3. Test Installation

```bash
# Run tests to verify setup
pytest tests/ -v

# Run with warnings ignored (in case of deprecation warnings)
pytest tests/ -v -p no:warnings

# Run quick start example
python examples/quickstart.py

# Test parser on current project
python -m src.parser.code_parser
```

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

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_parser.py -v
```

## Project Components

### 1. Parser Module (`src/parser/`)
- Parses Python code using Tree-sitter
- Extracts functions, classes, methods, imports
- Provides file-level and repository-level analysis

### 2. Summarizer Module (`src/summarizer/`)
- File-level summarization using OpenAI
- Progressive summarization for large repos
- Repository-level architecture summaries

### 3. RAG Module (`src/rag/`)
- FAISS vector store for semantic search
- BM25 for keyword-based search
- Hybrid search combining both approaches

### 4. Chatbot Module (`src/chatbot/`)
- RAG-based question answering
- Repository-aware responses
- Source attribution

### 5. Web Interface (`src/web/`)
- Flask-based documentation viewer
- Integrated chatbot in bottom-right
- File browsing and search

## Configuration

All configuration is centralized in `src/config.py`:

```python
# Key configurations
EMBEDDING_MODEL = "voyage-3"           # Voyage AI embedding model
LLM_MODEL = "gpt-4o"                   # or gpt-4-turbo, gpt-3.5-turbo
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RETRIEVAL = 5
HYBRID_SEARCH_ALPHA = 0.5  # 0=BM25, 1=semantic
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not set"**
   - Ensure `.env` file exists with valid API key
   - Check that `python-dotenv` is installed

2. **Tree-sitter parser errors**
   - Reinstall tree-sitter packages: `pip install --force-reinstall tree-sitter-python`

3. **FAISS installation issues on Mac**
   - Use `faiss-cpu` instead of `faiss-gpu`
   - Install via conda if pip fails: `conda install -c conda-forge faiss-cpu`

4. **Out of memory errors**
   - Reduce `CHUNK_SIZE` in config
   - Process repository in batches
   - Use smaller embedding model

## Summary of Setup 

1. **Set up API keys** - Add OpenAI and Voyage API keys to `.env`
2. **Run tests** - Verify installation with `pytest`
3. **Try example** - Run `python examples/quickstart.py`
4. **Test on small repo** - Generate docs for a small project

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)

