"""
Multi-book retrieval orchestrator for querying multiple religious texts simultaneously.
"""

from typing import List, Dict, Any, Optional
from src.book_manager import BookManager
from src.retrieval_engine import RetrievalEngine
from src.logger import get_logger

logger = get_logger(__name__)


class MultiBookRetrieval:
    """Orchestrate queries across multiple books."""
    
    def __init__(self, book_manager: BookManager):
        """
        Initialize multi-book retrieval.
        
        Args:
            book_manager: BookManager instance
        """
        self.book_manager = book_manager
        self.retrieval_engines: Dict[str, RetrievalEngine] = {}
        logger.info("MultiBookRetrieval initialized")
    
    def get_or_create_engine(self, book_id: str) -> Optional[RetrievalEngine]:
        """
        Get or create a retrieval engine for a book.
        
        Args:
            book_id: Book identifier
            
        Returns:
            RetrievalEngine instance or None if book not available
        """
        # Return cached engine if available
        if book_id in self.retrieval_engines:
            return self.retrieval_engines[book_id]
        
        # Try to get vector store for the book
        vector_store = self.book_manager.get_vector_store(book_id)
        if not vector_store:
            logger.warning(f"Could not load vector store for {book_id}")
            return None
        
        # Create and cache retrieval engine
        engine = RetrievalEngine(
            vector_store=vector_store,
            enable_conversation=True
        )
        self.retrieval_engines[book_id] = engine
        logger.info(f"Created retrieval engine for {book_id}")
        
        return engine
    
    def query_multiple_books(
        self,
        question: str,
        book_ids: List[str],
        k: Optional[int] = None,
        use_conversation_context: bool = True
    ) -> Dict[str, Any]:
        """
        Query multiple books simultaneously.
        
        Args:
            question: User's question
            book_ids: List of book IDs to query
            k: Number of results per book
            use_conversation_context: Whether to use conversation history
            
        Returns:
            Dictionary mapping book_id to query results
        """
        logger.info(f"Querying {len(book_ids)} books: {book_ids}")
        results = {}
        
        for book_id in book_ids:
            try:
                # Get or create engine for this book
                engine = self.get_or_create_engine(book_id)
                
                if not engine:
                    results[book_id] = {
                        "error": "vector_store_not_found",
                        "message": f"No vector store found for {self.book_manager.get_book_display_name(book_id)}",
                        "answer": None,
                        "sources": []
                    }
                    logger.warning(f"Skipping {book_id} - no vector store")
                    continue
                
                # Query the book
                logger.debug(f"Querying {book_id}...")
                result = engine.query(
                    question=question,
                    k=k,
                    use_conversation_context=use_conversation_context
                )
                
                # Add book metadata
                result['book_id'] = book_id
                result['book_name'] = self.book_manager.get_book_display_name(book_id)
                
                results[book_id] = result
                logger.info(f"Query successful for {book_id}: {result.get('num_sources', 0)} sources")
                
            except Exception as e:
                logger.error(f"Error querying {book_id}: {e}", exc_info=True)
                results[book_id] = {
                    "error": "query_failed",
                    "message": f"Error querying {book_id}: {str(e)}",
                    "answer": None,
                    "sources": [],
                    "book_id": book_id,
                    "book_name": self.book_manager.get_book_display_name(book_id)
                }
        
        logger.info(f"Multi-book query completed: {len(results)} results")
        return results
    
    def query_single_book(
        self,
        question: str,
        book_id: str,
        k: Optional[int] = None,
        use_conversation_context: bool = True
    ) -> Dict[str, Any]:
        """
        Query a single book (convenience method).
        
        Args:
            question: User's question
            book_id: Book identifier
            k: Number of results
            use_conversation_context: Whether to use conversation history
            
        Returns:
            Query result dictionary
        """
        results = self.query_multiple_books(
            question=question,
            book_ids=[book_id],
            k=k,
            use_conversation_context=use_conversation_context
        )
        return results.get(book_id, {})
    
    def clear_conversation(self, book_id: Optional[str] = None):
        """
        Clear conversation history.
        
        Args:
            book_id: Optional book ID to clear (None = clear all)
        """
        if book_id:
            if book_id in self.retrieval_engines:
                self.retrieval_engines[book_id].clear_conversation()
                logger.info(f"Cleared conversation for {book_id}")
        else:
            for engine in self.retrieval_engines.values():
                engine.clear_conversation()
            logger.info("Cleared all conversations")
    
    def clear_all_conversations(self):
        """Clear all conversation histories."""
        self.clear_conversation(None)

