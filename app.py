"""
Streamlit web interface for the RAG pipeline.
"""

import streamlit as st
import sys
from pathlib import Path
import time
from typing import Optional

# Removed PDF processing imports - now handled via CLI only
from src.vector_store import VectorStoreManager
from src.retrieval_engine import RetrievalEngine
from src.config import get_settings, validate_config, AVAILABLE_BOOKS
from src.logger import setup_logging, get_logger
from src.book_manager import BookManager
from src.multi_book_retrieval import MultiBookRetrieval

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Initialize logging
setup_logging()
logger = get_logger(__name__)


# Page configuration
st.set_page_config(
    page_title="Chat with Sacred Texts",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Simple CSS for consistent layout
st.markdown("""
<style>
    /* Basic styling only */
    .stChatMessage {
        margin-bottom: 1rem;
    }
    
    .stExpander {
        margin-top: 0.5rem;
    }
    
    /* Simple book selection styling */
    .stCheckbox > label {
        font-weight: 500;
    }
    
    /* Prevent horizontal scrolling */
    .stApp {
        overflow-x: hidden;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    # Legacy single vector store (for backward compatibility)
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = VectorStoreManager()
    
    if "retrieval_engine" not in st.session_state:
        st.session_state.retrieval_engine = None
    
    if "ingestion_stats" not in st.session_state:
        st.session_state.ingestion_stats = None
    
    if "kb_loaded" not in st.session_state:
        st.session_state.kb_loaded = False
    
    # Multi-book management
    if "book_manager" not in st.session_state:
        st.session_state.book_manager = BookManager()
        # Try to migrate legacy vector store
        st.session_state.book_manager.migrate_legacy_vector_store()
    
    if "multi_book_retrieval" not in st.session_state:
        st.session_state.multi_book_retrieval = MultiBookRetrieval(st.session_state.book_manager)
    
    if "selected_books" not in st.session_state:
        # Default to Bhagavad Gita for backward compatibility
        st.session_state.selected_books = ["bhagavad_gita"]
    
    # Chat-related state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "conversation_mode" not in st.session_state:
        st.session_state.conversation_mode = True
    
# Removed sidebar state tracking - keeping sidebar always expanded


def load_existing_vector_store():
    """Try to load an existing vector store."""
    if not st.session_state.kb_loaded:
        logger.info("Attempting to load existing vector store")
        with st.spinner("Loading existing knowledge base..."):
            if st.session_state.vector_store.load():
                logger.info("Vector store loaded successfully")
                st.session_state.retrieval_engine = RetrievalEngine(
                    vector_store=st.session_state.vector_store
                )
                st.session_state.kb_loaded = True
                return True
            else:
                logger.warning("No existing vector store found")
    return st.session_state.kb_loaded


# Removed ingestion functions - now handled via CLI only


def display_multi_book_response(results: dict):
    """
    Display responses from multiple books side-by-side.
    
    Args:
        results: Dictionary mapping book_id to query results
    """
    num_books = len(results)
    cols = st.columns(num_books)
    
    for idx, (book_id, result) in enumerate(results.items()):
        with cols[idx]:
            # Book header
            book_name = result.get('book_name', book_id)
            st.markdown(f"### 📖 {book_name}")
            st.divider()
            
            # Display answer or error
            if result.get("error"):
                st.error(result.get("message", "An error occurred"))
            elif result.get("answer"):
                st.write(result["answer"])
                
                # Display sources
                if result.get("sources"):
                    with st.expander(f"📚 Sources ({len(result['sources'])})"):
                        for source_idx, source in enumerate(result["sources"], 1):
                            st.caption(f"**Source {source_idx}:** {source.get('title', 'Chunk')}")
                            st.caption(f"Pages: {source['pages']} | Distance: {source['distance']:.4f}")
                            if source_idx < len(result["sources"]):
                                st.caption("---")
            else:
                st.warning("No response available")


def query_tab():
    """Render the question answering interface with chat mode."""
    # Book selection at the top
    available_books = st.session_state.book_manager.get_book_list()
    loaded_books = [book for book in available_books if book['has_vector_store']]
    
    if not loaded_books:
        st.error("⚠️ No books available. Please add books using CLI first.")
        st.info("💡 Use: `python pipeline.py path/to/pdf --book-id book_name`")
        return
    
    # Simple book selection
    st.subheader("📚 Select Books to Query")
    
    selected_books = []
    for book in loaded_books:
        book_id = book['id']
        book_name = book['display_name']
        is_loaded = book['loaded']
        
        # Default selection: first book if none selected, or previously selected books
        default_value = (
            book_id in (st.session_state.selected_books if st.session_state.selected_books else [loaded_books[0]['id']])
        )
        
        is_selected = st.checkbox(
            f"{book_name} {'✅' if is_loaded else '📥'}",
            value=default_value,
            key=f"book_checkbox_{book_id}"
        )
        
        if is_selected:
            selected_books.append(book_id)
    
    # Validation: At least one book must be selected
    if not selected_books:
        st.error("⚠️ Please select at least one book to chat with.")
        return
    
    # Simple settings
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.conversation_mode = st.toggle("💬 Conversation Mode", value=st.session_state.conversation_mode)
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
            st.session_state.multi_book_retrieval.clear_all_conversations()
            st.rerun()
    
    # Update session state
    st.session_state.selected_books = selected_books
    
    # Load selected books if not already loaded
    for book_id in selected_books:
        if not st.session_state.book_manager.is_book_loaded(book_id):
            with st.spinner(f"Loading {st.session_state.book_manager.get_book_display_name(book_id)}..."):
                st.session_state.book_manager.load_book(book_id)
    
    # Advanced settings
    with st.expander("⚙️ Advanced Options"):
        top_k = st.slider("Number of sources to retrieve", min_value=1, max_value=10, value=5)
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                # For assistant messages with multiple books
                if "results" in message and len(message["results"]) > 1:
                    display_multi_book_response(message["results"])
                else:
                    # Single book response
                    st.write(message["content"])
                    if "sources" in message and message["sources"]:
                        with st.expander(f"📚 Sources ({len(message['sources'])})"):
                            for idx, source in enumerate(message["sources"], 1):
                                st.caption(f"**Source {idx}:** {source.get('title', 'Chunk')} (Page {source['pages']})")
    
    # Chat input - part of the chat panel
    query = st.chat_input("Ask a question about the selected books...")
    
    if query:
        # Add user message to chat
        st.session_state.chat_messages.append({"role": "user", "content": query})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(query)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Query all selected books
                    results = st.session_state.multi_book_retrieval.query_multiple_books(
                        question=query,
                        book_ids=selected_books,
                        k=top_k,
                        use_conversation_context=st.session_state.conversation_mode
                    )
                    
                    # Display based on number of books
                    if len(selected_books) == 1:
                        # Single book display
                        book_id = selected_books[0]
                        result = results[book_id]
                        
                        if result.get("error"):
                            st.error(result.get("message", "An error occurred"))
                        else:
                            st.write(result["answer"])
                            
                            # Add to chat history
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": result["answer"],
                                "sources": result.get("sources", []),
                                "book_id": book_id
                            })
                            
                            # Display sources
                            if result.get("sources"):
                                with st.expander(f"📚 Sources ({len(result['sources'])})"):
                                    for idx, source in enumerate(result["sources"], 1):
                                        col1, col2 = st.columns([2, 1])
                                        with col1:
                                            st.caption(f"**{source.get('title', 'Chunk')}**")
                                            st.caption(f"Distance: {source['distance']:.4f}")
                                        with col2:
                                            st.caption(f"Pages: {source['pages']}")
                    else:
                        # Multi-book side-by-side display
                        display_multi_book_response(results)
                        
                        # Add to chat history
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": f"Responses from {len(selected_books)} books",
                            "results": results
                        })
                    
                    logger.info(f"Chat query successful for {len(selected_books)} books")
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": []
                    })
                    logger.error(f"Chat query failed: {str(e)}", exc_info=True)
        
        # Rerun to show the new message
        st.rerun()


def answer_question(query: str, top_k: int):
    """Process a user question and display the answer."""
    logger.info(f"Processing user question (top_k={top_k}): {query[:100]}...")
    try:
        with st.spinner("🤔 Thinking..."):
            result = st.session_state.retrieval_engine.query(query, k=top_k)
        
        logger.info(f"Answer generated successfully: {result['num_sources']} sources used")
        
        # Display answer
        st.subheader("💡 Answer")
        st.write(result["answer"])
        
        # Display sources
        st.divider()
        st.subheader(f"📚 Sources ({result['num_sources']})")
        
        for idx, source in enumerate(result["sources"], 1):
            with st.expander(f"Source {idx}: {source.get('title', 'Chunk')} - Distance: {source['distance']:.4f}"):
                # Metadata
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Type:** {source['type']}")
                    st.write(f"**Pages:** {source['pages']}")
                
                with col2:
                    if source['type'] == 'knowledge_group':
                        st.write(f"**Theme:** {source.get('theme', 'N/A')}")
                        st.write(f"**Importance:** {source.get('importance', 'N/A')}")
                
                # Preview
                st.text_area(
                    "Content Preview",
                    value=source["preview"],
                    height=150,
                    key=f"source_{idx}",
                )
                
                # Summary for groups
                if source['type'] == 'knowledge_group' and source.get('summary'):
                    st.info(f"**Summary:** {source['summary']}")
        
    except Exception as e:
        logger.error(f"Error during question answering: {str(e)}", exc_info=True)
        st.error(f"❌ Error during retrieval: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.title("📚 Multi-Religious RAG")
        st.write("Chat with Multiple Sacred Texts")
        
        st.divider()
        
        # Available Books Status
        st.subheader("📖 Available Books")
        book_list = st.session_state.book_manager.get_book_list()
        
        for book in book_list:
            if book['has_vector_store']:
                status = "✅" if book['loaded'] else "📥"
                st.text(f"{status} {book['name']}")
            else:
                st.text(f"⭕ {book['name']} (not ingested)")
        
        st.divider()
        
        # Selected Books
        if st.session_state.selected_books:
            st.subheader("🎯 Currently Selected")
            for book_id in st.session_state.selected_books:
                book_name = st.session_state.book_manager.get_book_display_name(book_id)
                st.text(f"• {book_name.split('(')[0].strip()}")
        
        st.divider()
        
        # Actions
        st.subheader("🔄 Actions")
        
        if st.button("📂 Load All Available Books"):
            with st.spinner("Loading books..."):
                results = st.session_state.book_manager.load_all_available_books()
                loaded_count = sum(results.values())
                if loaded_count > 0:
                    st.success(f"✓ Loaded {loaded_count} books!")
                    st.rerun()
                else:
                    st.warning("No books found to load")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = []
            st.session_state.multi_book_retrieval.clear_all_conversations()
            st.success("Chat cleared")
            st.rerun()
        
        st.divider()
        
        # Add books info
        st.subheader("📥 Add New Books")
        st.caption("Use CLI to add new religious texts:")
        st.code("python pipeline.py path/to/pdf --book-id book_name", language="bash")
        
        st.divider()
        
        # Settings info
        st.subheader("⚙️ Configuration")
        try:
            settings = get_settings()
            st.text(f"Model: {settings.openrouter_model.split('/')[-1]}")
            st.text(f"Embeddings: {settings.embedding_model.split('/')[-1]}")
            st.text(f"Chunk Size: {settings.chunk_size}")
        except:
            st.error("Configuration not loaded")


def main():
    """Main application entry point."""
    logger.info("=" * 80)
    logger.info("Streamlit app started")
    logger.info("=" * 80)
    
    # Initialize
    initialize_session_state()
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        st.error(f"❌ Configuration Error: {e}")
        st.info("Please create a .env file with your OPENROUTER_API_KEY")
        st.stop()
    
    # Try to load existing vector store on first run
    if not st.session_state.kb_loaded:
        logger.debug("Checking for existing vector store on startup")
        load_existing_vector_store()
    
    # Render sidebar
    sidebar()
    
    # Main content - simple layout
    st.title("💬 Chat with Sacred Texts")
    st.write("Ask questions and get answers from multiple religious texts simultaneously")
    
    # Display chat interface
    query_tab()


if __name__ == "__main__":
    main()

