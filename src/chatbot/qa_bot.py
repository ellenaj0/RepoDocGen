"""
Question-answering chatbot using RAG over repository documentation
"""

from openai import OpenAI
from typing import List, Dict, Optional

from src.config import Config
from src.rag.hybrid_search import HybridSearch
from src.rag.vector_store import Document


class QABot:
    """RAG-based QA bot for repository questions"""

    def __init__(
        self,
        hybrid_search: HybridSearch,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize QA bot

        Args:
            hybrid_search: HybridSearch instance for retrieval
            api_key: OpenAI API key
            model: Model name to use
        """
        self.hybrid_search = hybrid_search
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model_name = model or Config.LLM_MODEL

        self.client = OpenAI(api_key=self.api_key)

        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS

        # Conversation history
        self.history: List[Dict[str, str]] = []

    def query(self, question: str, top_k: int = None) -> Dict[str, any]:
        """
        Answer a question about the repository

        Args:
            question: User's question
            top_k: Number of relevant documents to retrieve

        Returns:
            Dict with 'answer', 'sources', and 'confidence'
        """
        if top_k is None:
            top_k = Config.TOP_K_RETRIEVAL

        # Retrieve relevant documents
        results = self.hybrid_search.search(question, top_k=top_k)

        if not results:
            return {
                "answer": "I don't have enough information to answer this question.",
                "sources": [],
                "confidence": 0.0,
            }

        # Build context from retrieved documents
        context = self._build_context(results)

        # Generate answer
        prompt = self._build_qa_prompt(question, context)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            answer = response.choices[0].message.content

            # Extract sources
            sources = self._format_sources(results)

            # Store in history
            self.history.append({"question": question, "answer": answer})

            return {
                "answer": answer,
                "sources": sources,
                "confidence": results[0][1] if results else 0.0,  # Top score
            }

        except Exception as e:
            print(f"Error generating answer: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }

    def _build_context(self, results: List[tuple]) -> str:
        """Build context string from retrieved documents"""
        context_parts = []

        for i, (doc, score) in enumerate(results, 1):
            metadata = doc.metadata
            file_info = f"File: {metadata.get('file_path', 'Unknown')}"
            if "line_range" in metadata:
                file_info += f" (lines {metadata['line_range']})"

            context_parts.append(f"[Source {i}] {file_info}\n{doc.content}\n")

        return "\n".join(context_parts)

    def _build_qa_prompt(self, question: str, context: str) -> str:
        """Build prompt for QA generation"""
        return f"""You are a helpful assistant analyzing a code repository. Answer the user's question based on the provided context from the repository.

Context from repository:
{context}

User Question: {question}

Instructions:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say so
3. Reference specific files and line numbers when relevant
4. Be concise but complete
5. If asked about code location, cite the file and lines
6. If asked about functionality, explain what the code does

Answer:"""

    def _format_sources(self, results: List[tuple]) -> List[Dict]:
        """Format sources for display"""
        sources = []
        for doc, score in results:
            metadata = doc.metadata
            sources.append(
                {
                    "file": metadata.get("file_path", "Unknown"),
                    "line_range": metadata.get("line_range", "N/A"),
                    "type": metadata.get("element_type", "code"),
                    "relevance": float(score),
                    "preview": (
                        doc.content 
                    ),
                }
            )
        return sources

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.history

    def clear_history(self):
        """Clear conversation history"""
        self.history.clear()


def main():
    """Test the QA bot"""
    from src.rag.vector_store import VectorStore, Document
    from src.rag.hybrid_search import HybridSearch

    # Create test repository documents
    docs = [
        Document(
            id="1",
            content="def calculate_sum(a, b):\n    '''Calculate sum of two numbers'''\n    return a + b",
            metadata={
                "file_path": "src/math_utils.py",
                "line_range": "1-3",
                "element_type": "function",
            },
        ),
        Document(
            id="2",
            content="class UserManager:\n    def create_user(self, name, email):\n        '''Create a new user'''\n        pass",
            metadata={
                "file_path": "src/models/user.py",
                "line_range": "10-15",
                "element_type": "class",
            },
        ),
        Document(
            id="3",
            content="The calculate_sum function is used throughout the application for basic arithmetic operations",
            metadata={
                "file_path": "docs/architecture.md",
                "element_type": "documentation",
            },
        ),
    ]

    # Initialize components
    vector_store = VectorStore()
    hybrid_search = HybridSearch(vector_store)
    hybrid_search.index_documents(docs)

    # Create QA bot
    bot = QABot(hybrid_search)

    # Test queries
    questions = [
        "Where is the calculate_sum function defined?",
        "How do I create a new user?",
        "What does calculate_sum do?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print(f"{'='*60}")

        result = bot.query(question)

        print(f"\nA: {result['answer']}")
        print(f"\nConfidence: {result['confidence']:.2f}")
        print("\nSources:")
        for i, source in enumerate(result["sources"], 1):
            print(f"  {i}. {source['file']} (lines {source['line_range']})")


if __name__ == "__main__":
    main()
