"""
Tests for vector store module
"""

import pytest
from src.rag.vector_store import VectorStore, Document

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestVectorStore:
    """Test suite for VectorStore"""

    @pytest.fixture
    def store(self):
        """Create vector store instance"""
        return VectorStore()

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents"""
        return [
            Document(
                id="1",
                content="This is a function that calculates sum",
                metadata={"file": "math.py"},
            ),
            Document(
                id="2",
                content="This is a class for user management",
                metadata={"file": "user.py"},
            ),
        ]

    def test_initialization(self, store):
        """Test vector store initializes"""
        assert store is not None
        assert store.index is not None
        assert len(store.documents) == 0

    def test_add_documents(self, store, sample_documents):
        """Test adding documents"""
        store.add_documents(sample_documents)

        assert len(store.documents) == 2
        assert store.index.ntotal == 2

    def test_search(self, store, sample_documents):
        """Test searching documents"""
        store.add_documents(sample_documents)

        results = store.search("sum calculation", top_k=1)

        assert len(results) > 0
        doc, score = results[0]
        assert doc.id in ["1", "2"]
        assert 0 <= score <= 1

    def test_get_document(self, store, sample_documents):
        """Test retrieving document by ID"""
        store.add_documents(sample_documents)

        doc = store.get_document("1")
        assert doc is not None
        assert doc.id == "1"

    def test_clear(self, store, sample_documents):
        """Test clearing store"""
        store.add_documents(sample_documents)
        store.clear()

        assert len(store.documents) == 0
        assert store.index.ntotal == 0
