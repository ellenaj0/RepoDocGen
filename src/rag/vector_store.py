"""
Vector store implementation using FAISS or Qdrant
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import faiss
import voyageai

from src.config import Config


@dataclass
class Document:
    """Represents a document chunk in the vector store"""

    id: str
    content: str
    metadata: Dict  # {file_path, language, element_type, line_range, etc.}
    embedding: Optional[np.ndarray] = None


class VectorStore:
    """Vector database for storing and retrieving code embeddings"""

    def __init__(
        self,
        embedding_model: str = None,
        dimension: int = None,
        use_gpu: bool = False,
    ):
        """Initialize vector store with embedding model"""
        self.embedding_model_name = embedding_model or Config.EMBEDDING_MODEL
        self.dimension = dimension or Config.EMBEDDING_DIMENSION
        self.use_gpu = use_gpu

        # Initialize Voyage AI client
        print(f"Initializing Voyage AI embedding model: {self.embedding_model_name}")
        if not Config.VOYAGE_API_KEY:
            raise ValueError("VOYAGE_API_KEY not set in environment")
        self.voyage_client = voyageai.Client(api_key=Config.VOYAGE_API_KEY)

        # Initialize FAISS index
        if self.use_gpu and faiss.get_num_gpus() > 0:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.index_cpu_to_all_gpus(self.index)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

        # Store documents (ID -> Document mapping)
        self.documents: Dict[str, Document] = {}
        self.id_to_idx: Dict[str, int] = {}  # Map doc ID to FAISS index

    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        if not documents:
            return

        print(f"Adding {len(documents)} documents to vector store...")

        # Generate embeddings using Voyage AI
        texts = [doc.content for doc in documents]
        print(f"Generating embeddings for {len(texts)} documents...")
        result = self.voyage_client.embed(
            texts, model=self.embedding_model_name, input_type="document"
        )
        embeddings = result.embeddings

        # Add to FAISS
        embeddings_np = np.array(embeddings).astype("float32")
        start_idx = self.index.ntotal
        self.index.add(embeddings_np)

        # Store documents
        for i, doc in enumerate(documents):
            doc.embedding = embeddings_np[i]
            self.documents[doc.id] = doc
            self.id_to_idx[doc.id] = start_idx + i

        print(f"✓ Added {len(documents)} documents. Total: {self.index.ntotal}")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents using semantic search"""
        if self.index.ntotal == 0:
            return []

        # Encode query using Voyage AI
        result = self.voyage_client.embed(
            [query], model=self.embedding_model_name, input_type="query"
        )
        query_embedding = np.array([result.embeddings[0]]).astype("float32")

        # Search FAISS
        distances, indices = self.index.search(query_embedding, top_k)

        # Get documents
        results = []
        idx_to_id = {v: k for k, v in self.id_to_idx.items()}

        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx in idx_to_id:
                doc_id = idx_to_id[idx]
                doc = self.documents[doc_id]
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                results.append((doc, similarity))

        return results

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve document by ID"""
        return self.documents.get(doc_id)

    def clear(self):
        """Clear all documents"""
        self.index.reset()
        self.documents.clear()
        self.id_to_idx.clear()

    def save(self, path: str):
        """Save index to disk"""
        import pickle

        faiss.write_index(self.index, f"{path}/faiss.index")
        with open(f"{path}/documents.pkl", "wb") as f:
            pickle.dump((self.documents, self.id_to_idx), f)
        print(f"✓ Saved vector store to {path}")

    def load(self, path: str):
        """Load index from disk"""
        import pickle

        self.index = faiss.read_index(f"{path}/faiss.index")
        with open(f"{path}/documents.pkl", "rb") as f:
            self.documents, self.id_to_idx = pickle.load(f)
        print(f"✓ Loaded vector store from {path}")

    def get_stats(self) -> Dict:
        """Get statistics about vector store"""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal,
            "dimension": self.dimension,
            "model": self.embedding_model_name,
        }


def main():
    """Test the vector store"""
    # Create test documents
    docs = [
        Document(
            id="1",
            content="def calculate_sum(a, b): return a + b",
            metadata={"file": "math.py", "type": "function"},
        ),
        Document(
            id="2",
            content="class UserManager: def create_user(self, name): pass",
            metadata={"file": "user.py", "type": "class"},
        ),
        Document(
            id="3",
            content="import numpy as np; arr = np.array([1,2,3])",
            metadata={"file": "data.py", "type": "import"},
        ),
    ]

    # Initialize and add documents
    store = VectorStore()
    store.add_documents(docs)

    # Search
    results = store.search("function that adds numbers", top_k=2)

    print("\n=== Search Results ===")
    for doc, score in results:
        print(f"Score: {score:.3f}")
        print(f"Content: {doc.content}")
        print(f"Metadata: {doc.metadata}\n")


if __name__ == "__main__":
    main()
