"""
Retrieval and QA engine with LLM-powered answer generation.
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from openai import OpenAI
from src.vector_store import VectorStoreManager
from src.config import get_settings, validate_config
from src.logger import get_logger
from src.conversation_manager import ConversationManager

logger = get_logger(__name__)


class RetrievalEngine:
    """Query interface with retrieval and answer generation."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStoreManager] = None,
        model: Optional[str] = None,
        enable_conversation: bool = True,
        book_id: Optional[str] = None,
    ):
        """
        Initialize the retrieval engine.
        
        Args:
            vector_store: Vector store manager instance
            model: OpenRouter model to use
            enable_conversation: Enable conversation history management
            book_id: Optional book identifier for metadata
        """
        logger.info(f"Initializing RetrievalEngine (book_id: {book_id})")
        validate_config()
        settings = get_settings()
        
        self.vector_store = vector_store or VectorStoreManager()
        self.model = model or settings.openrouter_model
        self.top_k = settings.top_k_results
        self.book_id = book_id
        
        # Conversation management
        self.enable_conversation = enable_conversation
        self.conversation = ConversationManager() if enable_conversation else None
        
        logger.info(f"Model: {self.model}, Top-k: {self.top_k}, Conversation: {enable_conversation}")
        
        # Initialize OpenAI client with OpenRouter
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
        logger.debug("OpenAI client initialized for retrieval")
    
    def _format_context(self, results: List[Tuple[Document, float]]) -> str:
        """
        Format retrieved documents as context for the LLM.
        
        Args:
            results: List of (document, distance) tuples
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for idx, (doc, distance) in enumerate(results, 1):
            metadata = doc.metadata
            
            # Format based on whether it's a knowledge group or chunk
            if metadata.get("type") == "knowledge_group":
                header = f"[Group {idx}: {metadata.get('title', 'Untitled')}]"
                summary = f"Theme: {metadata.get('theme', 'N/A')}"
                pages = f"Pages: {metadata.get('pages', [])}"
                context_parts.append(f"{header}\n{summary}\n{pages}\n\n{doc.page_content}")
            else:
                header = f"[Chunk {idx} - Page {metadata.get('page', 'N/A')}]"
                context_parts.append(f"{header}\n{doc.page_content}")
            
            context_parts.append("\n" + "="*80 + "\n")
        
        return "\n".join(context_parts)
    
    def _create_qa_prompt(self, query: str, context: str) -> List[Dict[str, str]]:
        """
        Create a prompt for question answering.
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            List of message dictionaries for the LLM
        """
        system_prompt = """You are a knowledgeable assistant helping users understand documents through question answering.

Your role:
1. Answer questions based ONLY on the provided context
2. Provide accurate, detailed, and well-structured answers
3. Cite specific parts of the context when relevant
4. If the context doesn't contain enough information, say so clearly
5. Maintain the original meaning and nuance from the source material

Guidelines:
- Be comprehensive but concise
- Use quotes when directly referencing the text
- Explain complex concepts clearly
- If asked about page numbers or sources, refer to the metadata provided
"""
        
        user_prompt = f"""Based on the following context from the document, please answer this question:

QUESTION: {query}

CONTEXT:
{context}

Please provide a thorough answer based on the context above."""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    def _reformulate_query(self, query: str, conversation_context: str) -> str:
        """
        Reformulate a follow-up question using conversation context.
        
        Args:
            query: Current user query
            conversation_context: Previous conversation history
            
        Returns:
            Reformulated standalone question
        """
        if not conversation_context:
            return query  # No context, return as-is
        
        logger.debug(f"Reformulating query with conversation context")
        
        prompt = f"""Given the following conversation history, reformulate the follow-up question into a standalone question that captures all necessary context.

Conversation History:
{conversation_context}

Follow-up Question: {query}

Reformulated Standalone Question:"""
        
        try:
            # Use simple messages for reformulation
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Low temperature for consistency
                max_tokens=200,  # Keep it concise
            )
            
            reformulated = response.choices[0].message.content.strip()
            logger.info(f"Query reformulated: '{query}' -> '{reformulated}'")
            return reformulated
            
        except Exception as e:
            logger.warning(f"Query reformulation failed: {e}, using original query")
            return query  # Fall back to original on error
    
    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Call the LLM for answer generation.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            LLM response text
        """
        try:
            logger.debug(f"Calling LLM for answer generation with model: {self.model}")
            
            # Models that support system messages (Claude, GPT-4, etc.)
            models_with_system_support = [
                'anthropic/', 'openai/', 'meta-llama/', 'mistralai/', 'cohere/'
            ]
            
            supports_system = any(self.model.startswith(prefix) for prefix in models_with_system_support)
            
            # If model doesn't support system messages, merge system into user message
            if not supports_system and len(messages) >= 2 and messages[0].get('role') == 'system':
                logger.debug(f"Model {self.model} may not support system messages, merging into user prompt")
                system_content = messages[0]['content']
                user_content = messages[1]['content']
                merged_messages = [
                    {
                        "role": "user",
                        "content": f"{system_content}\n\n{user_content}"
                    }
                ]
                messages = merged_messages
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            answer = response.choices[0].message.content
            logger.debug(f"LLM response received: {len(answer)} characters")
            return answer
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error calling OpenRouter: {str(e)}")
    
    def query(
        self,
        question: str,
        k: Optional[int] = None,
        use_conversation_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Query the knowledge base and generate an answer.
        
        Args:
            question: User's question
            k: Number of results to retrieve (defaults to config)
            use_conversation_context: Whether to use conversation history for context
            
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing query: '{question[:100]}...'")
        
        if self.vector_store.is_empty():
            logger.warning("Query attempted on empty knowledge base")
            return {
                "answer": "The knowledge base is empty. Please ingest a document first.",
                "sources": [],
                "error": "empty_kb",
            }
        
        k = k or self.top_k
        logger.debug(f"Retrieving top-{k} results")
        
        # Reformulate query using conversation context if enabled
        search_query = question
        if use_conversation_context and self.conversation and len(self.conversation) > 0:
            conversation_context = self.conversation.get_conversation_context(last_n=3)
            search_query = self._reformulate_query(question, conversation_context)
            logger.info("Using reformulated query for retrieval")
        
        # Retrieve relevant documents
        results = self.vector_store.search(search_query, k=k)
        
        if not results:
            logger.warning("No relevant results found for query")
            answer_result = {
                "answer": "No relevant information found for your question.",
                "sources": [],
                "error": "no_results",
                "query": question,
                "num_sources": 0,
            }
            
            # Store in conversation history even for no results
            if self.conversation:
                self.conversation.add_exchange(question, answer_result["answer"])
            
            return answer_result
        
        logger.info(f"Retrieved {len(results)} results, generating answer...")
        
        # Format context
        context = self._format_context(results)
        logger.debug(f"Context formatted: {len(context)} characters")
        
        # Create prompt and get answer
        # Include conversation history in the prompt if available
        messages = self._create_qa_prompt(question, context)
        
        # Add conversation history to system prompt if enabled
        if use_conversation_context and self.conversation and len(self.conversation) > 0:
            history_text = self.conversation.get_history_text(last_n=3, include_sources=False)
            # Prepend history to system message
            if messages and messages[0].get('role') == 'system':
                messages[0]['content'] = (
                    f"{messages[0]['content']}\n\n"
                    f"Conversation History (for context only):\n{history_text}"
                )
        
        answer = self._call_llm(messages)
        
        # Format source information
        sources = []
        for doc, distance in results:
            metadata = doc.metadata
            source_info = {
                "type": metadata.get("type", "chunk"),
                "title": metadata.get("title", ""),
                "pages": metadata.get("pages", [metadata.get("page", "N/A")]),
                "distance": distance,
                "preview": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
            }
            
            if metadata.get("type") == "knowledge_group":
                source_info.update({
                    "theme": metadata.get("theme", ""),
                    "summary": metadata.get("summary", ""),
                    "importance": metadata.get("importance", "medium"),
                })
            
            sources.append(source_info)
        
        logger.info(f"Query completed successfully: {len(sources)} sources cited")
        
        result = {
            "answer": answer,
            "sources": sources,
            "query": question,
            "num_sources": len(sources),
            "book_id": self.book_id,
        }
        
        # Store exchange in conversation history
        if self.conversation:
            self.conversation.add_exchange(
                user_query=question,
                assistant_response=answer,
                sources=sources,
                metadata={
                    "num_sources": len(sources),
                    "reformulated": search_query != question,
                    "search_query": search_query if search_query != question else None
                }
            )
            logger.debug("Exchange added to conversation history")
        
        return result
    
    def retrieve_only(self, query: str, k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents without generating an answer.
        
        Args:
            query: Search query
            k: Number of results to retrieve
            
        Returns:
            List of retrieved documents with metadata
        """
        logger.debug(f"Retrieve-only mode for query: '{query[:50]}...'")
        k = k or self.top_k
        results = self.vector_store.search(query, k=k)
        
        retrieved = []
        for doc, distance in results:
            retrieved.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "distance": distance,
            })
        
        logger.info(f"Retrieved {len(retrieved)} documents (no answer generation)")
        return retrieved
    
    def clear_conversation(self):
        """Clear conversation history."""
        if self.conversation:
            self.conversation.clear()
            logger.info("Conversation history cleared")
    
    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            last_n: Number of recent exchanges to return
            
        Returns:
            List of conversation exchanges
        """
        if self.conversation:
            return self.conversation.get_history(last_n)
        return []
    
    def export_conversation(self) -> List[Dict[str, Any]]:
        """
        Export conversation history.
        
        Returns:
            Complete conversation history
        """
        if self.conversation:
            return self.conversation.export_history()
        return []


def create_retrieval_engine(vector_store: Optional[VectorStoreManager] = None) -> RetrievalEngine:
    """
    Create a retrieval engine instance.
    
    Args:
        vector_store: Optional vector store instance
        
    Returns:
        RetrievalEngine instance
    """
    return RetrievalEngine(vector_store=vector_store)

