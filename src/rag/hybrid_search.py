"""
Hybrid search combining BM25 (keyword-based) and semantic search
"""

from typing import List, Tuple
from rank_bm25 import BM25Okapi
import numpy as np

from src.rag.vector_store import Document, VectorStore
from src.config import Config


class HybridSearch:
    """Hybrid search combining BM25 and semantic similarity"""

    def __init__(self, vector_store: VectorStore, alpha: float = None):
        """
        Initialize hybrid search

        Args:
            vector_store: VectorStore instance for semantic search
            alpha: Weight for combining scores (0=full BM25, 1=full semantic)
        """
        self.vector_store = vector_store
        self.alpha = alpha if alpha is not None else Config.HYBRID_SEARCH_ALPHA

        # BM25 index
        self.bm25 = None
        self.doc_ids = []  # Maintain order of documents for BM25

    def index_documents(self, documents: List[Document]):
        """Index documents for both BM25 and semantic search"""

        # Add to vector store
        self.vector_store.add_documents(documents)

        # Build BM25 index
        print("Building BM25 index...")
        tokenized_docs = [doc.content.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        self.doc_ids = [doc.id for doc in documents]
        print(f"✓ Indexed {len(documents)} documents for BM25")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """
        Perform hybrid search

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (Document, combined_score) tuples
        """
        if not self.bm25:
            # Fallback to semantic only if BM25 not initialized
            return self.vector_store.search(query, top_k)

        # Get BM25 scores
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Normalize BM25 scores to [0, 1]
        if bm25_scores.max() > 0:
            bm25_scores_norm = bm25_scores / bm25_scores.max()
        else:
            bm25_scores_norm = bm25_scores

        # Get semantic search scores
        # Retrieve more candidates for reranking
        semantic_results = self.vector_store.search(query, top_k=top_k * 2)

        # Combine scores
        combined_scores = {}

        # Add BM25 scores
        for doc_id, score in zip(self.doc_ids, bm25_scores_norm):
            combined_scores[doc_id] = (1 - self.alpha) * score

        # Add semantic scores
        for doc, score in semantic_results:
            if doc.id in combined_scores:
                combined_scores[doc.id] += self.alpha * score
            else:
                combined_scores[doc.id] = self.alpha * score

        # Sort by combined score
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        # Retrieve documents
        results = []
        for doc_id, score in sorted_ids:
            doc = self.vector_store.get_document(doc_id)
            if doc:
                results.append((doc, score))

        return results

    def set_alpha(self, alpha: float):
        """Change the hybrid search weight (0=BM25, 1=semantic)"""
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")
        self.alpha = alpha


def main():
    """Test hybrid search"""
    from src.rag.vector_store import VectorStore, Document

    # Create test documents
    docs = [
        Document(
            id="1",
            content="This function calculates the sum of two numbers using addition operator",
            metadata={"file": "math.py"},
        ),
        Document(
            id="2",
            content="Class for managing user authentication and authorization",
            metadata={"file": "auth.py"},
        ),
        Document(
            id="3",
            content="Function to add items to shopping cart",
            metadata={"file": "cart.py"},
        ),
        Document(
            id="4",
            content="Sum function implementation in Python for numeric addition",
            metadata={"file": "utils.py"},
        ),
    ]

    # Initialize
    vector_store = VectorStore()
    hybrid_search = HybridSearch(vector_store, alpha=0.5)
    hybrid_search.index_documents(docs)

    # Test search
    query = "sum addition function"
    print(f"\n=== Hybrid Search Results for: '{query}' ===\n")

    results = hybrid_search.search(query, top_k=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. Score: {score:.3f}")
        print(f"   Content: {doc.content}")
        print(f"   File: {doc.metadata['file']}\n")


if __name__ == "__main__":
    main()
