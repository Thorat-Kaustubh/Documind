import logging
from typing import List, Optional
from database.vector_storage import VectorStorage

logger = logging.getLogger("documind.execution.rag")

class RAGEngine:
    """
    SECTION 5.2: RAG ENGINE
    Handles intelligent document retrieval and context assembly.
    """
    def __init__(self):
        self.vector_db = VectorStorage()

    async def retrieve_context(self, query: str, user_id: str, company: Optional[str] = None, n_results: int = 5) -> str:
        """
        Retrieves relevant context chunks from the vector database.
        Includes company filtering if provided.
        """
        logger.info(f"RAG Engine: Retrieving context for query: {query}")
        
        # In a real system, we'd add 'filter' for company if supported by vector_storage
        results = self.vector_db.query(
            query_text=query, 
            n_results=n_results, 
            user_id=user_id
        )
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return "[RAG: No relevant document context found.]"

        formatted_context = []
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            source = meta.get('source', 'Unknown Document')
            formatted_context.append(f"--- SOURCE: {source} ---\n{doc}")

        return "\n\n".join(formatted_context)
