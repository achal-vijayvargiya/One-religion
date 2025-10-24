"""
Conversation history management for multi-turn RAG interactions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


class ConversationManager:
    """Manage conversation history and context for multi-turn dialogues."""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation manager.
        
        Args:
            max_history: Maximum number of exchanges to keep in history
        """
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        logger.info(f"ConversationManager initialized with max_history={max_history}")
    
    def add_exchange(
        self,
        user_query: str,
        assistant_response: str,
        sources: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add a Q&A exchange to the conversation history.
        
        Args:
            user_query: User's question
            assistant_response: Assistant's answer
            sources: List of source documents used
            metadata: Additional metadata
        """
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_query,
            "assistant": assistant_response,
            "sources": sources or [],
            "metadata": metadata or {}
        }
        
        self.history.append(exchange)
        
        # Trim history if it exceeds max_history
        if len(self.history) > self.max_history:
            removed = self.history.pop(0)
            logger.debug(f"Removed oldest exchange from history: '{removed['user'][:50]}...'")
        
        logger.debug(f"Added exchange to history (total: {len(self.history)})")
    
    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            last_n: Number of recent exchanges to return (None = all)
            
        Returns:
            List of conversation exchanges
        """
        if last_n is None:
            return self.history.copy()
        return self.history[-last_n:]
    
    def get_history_text(self, last_n: int = 5, include_sources: bool = False) -> str:
        """
        Get conversation history as formatted text.
        
        Args:
            last_n: Number of recent exchanges to include
            include_sources: Whether to include source information
            
        Returns:
            Formatted conversation history string
        """
        history = self.get_history(last_n)
        
        if not history:
            return "No previous conversation."
        
        lines = ["Previous conversation:"]
        
        for i, exchange in enumerate(history, 1):
            lines.append(f"\nUser: {exchange['user']}")
            lines.append(f"Assistant: {exchange['assistant']}")
            
            if include_sources and exchange.get('sources'):
                source_count = len(exchange['sources'])
                lines.append(f"[Used {source_count} sources]")
        
        return "\n".join(lines)
    
    def get_conversation_context(self, last_n: int = 3) -> str:
        """
        Get conversation context for query reformulation.
        
        Args:
            last_n: Number of recent exchanges to include
            
        Returns:
            Formatted context string
        """
        history = self.get_history(last_n)
        
        if not history:
            return ""
        
        context_parts = []
        for exchange in history:
            context_parts.append(f"Q: {exchange['user']}")
            # Only include first 200 chars of answer for context
            answer = exchange['assistant'][:200]
            if len(exchange['assistant']) > 200:
                answer += "..."
            context_parts.append(f"A: {answer}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear all conversation history."""
        count = len(self.history)
        self.history.clear()
        logger.info(f"Conversation history cleared ({count} exchanges removed)")
    
    def export_history(self) -> List[Dict[str, Any]]:
        """
        Export conversation history for saving/analysis.
        
        Returns:
            Complete conversation history
        """
        return self.history.copy()
    
    def import_history(self, history: List[Dict[str, Any]]):
        """
        Import conversation history from saved data.
        
        Args:
            history: Previously exported conversation history
        """
        self.history = history[-self.max_history:]  # Respect max_history
        logger.info(f"Imported {len(self.history)} exchanges into conversation history")
    
    def get_last_query(self) -> Optional[str]:
        """
        Get the last user query.
        
        Returns:
            Last query or None if no history
        """
        if self.history:
            return self.history[-1]['user']
        return None
    
    def get_last_response(self) -> Optional[str]:
        """
        Get the last assistant response.
        
        Returns:
            Last response or None if no history
        """
        if self.history:
            return self.history[-1]['assistant']
        return None
    
    def __len__(self) -> int:
        """Return number of exchanges in history."""
        return len(self.history)
    
    def __repr__(self) -> str:
        """String representation of conversation manager."""
        return f"ConversationManager(history={len(self.history)}/{self.max_history})"

