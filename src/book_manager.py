"""
Book manager for handling multiple religious text vector stores.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from src.vector_store import VectorStoreManager
from src.config import AVAILABLE_BOOKS, get_vector_store_path, get_book_info
from src.logger import get_logger

logger = get_logger(__name__)


class BookManager:
    """Manage multiple book vector stores and metadata."""
    
    def __init__(self):
        """Initialize the book manager."""
        logger.info("Initializing BookManager")
        self.books = AVAILABLE_BOOKS.copy()
        self.vector_stores: Dict[str, VectorStoreManager] = {}
        self.loaded_books: List[str] = []
        logger.info(f"Available books: {list(self.books.keys())}")
    
    def get_book_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available books with their metadata.
        
        Returns:
            List of book information dictionaries
        """
        book_list = []
        for book_id, info in self.books.items():
            book_info = info.copy()
            book_info['id'] = book_id
            book_info['loaded'] = book_id in self.loaded_books
            book_info['has_vector_store'] = self._check_vector_store_exists(book_id)
            book_list.append(book_info)
        
        return book_list
    
    def _check_vector_store_exists(self, book_id: str) -> bool:
        """
        Check if a vector store exists for a book.
        
        Args:
            book_id: Book identifier
            
        Returns:
            True if vector store files exist
        """
        try:
            store_path = get_vector_store_path(book_id)
            index_file = store_path / "faiss.index"
            data_file = store_path / "documents.pkl"
            exists = index_file.exists() and data_file.exists()
            logger.debug(f"Vector store check for {book_id}: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking vector store for {book_id}: {e}")
            return False
    
    def load_book(self, book_id: str) -> bool:
        """
        Load a book's vector store.
        
        Args:
            book_id: Book identifier
            
        Returns:
            True if loaded successfully
        """
        if book_id not in self.books:
            logger.error(f"Unknown book ID: {book_id}")
            return False
        
        if book_id in self.loaded_books:
            logger.info(f"Book {book_id} already loaded")
            return True
        
        try:
            logger.info(f"Loading vector store for book: {book_id}")
            vector_store = VectorStoreManager(book_id=book_id)
            
            if vector_store.load():
                self.vector_stores[book_id] = vector_store
                self.loaded_books.append(book_id)
                logger.info(f"Successfully loaded {book_id}: {vector_store.index.ntotal} vectors")
                return True
            else:
                logger.warning(f"Vector store not found for {book_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading book {book_id}: {e}", exc_info=True)
            return False
    
    def load_all_available_books(self) -> Dict[str, bool]:
        """
        Load all books that have vector stores available.
        
        Returns:
            Dictionary mapping book_id to load success status
        """
        logger.info("Loading all available books")
        results = {}
        
        for book_id in self.books.keys():
            if self._check_vector_store_exists(book_id):
                results[book_id] = self.load_book(book_id)
            else:
                logger.debug(f"Skipping {book_id} - no vector store found")
                results[book_id] = False
        
        logger.info(f"Loaded {sum(results.values())}/{len(results)} books")
        return results
    
    def get_vector_store(self, book_id: str) -> Optional[VectorStoreManager]:
        """
        Get a loaded vector store for a book.
        
        Args:
            book_id: Book identifier
            
        Returns:
            VectorStoreManager instance or None
        """
        if book_id not in self.loaded_books:
            logger.warning(f"Book {book_id} not loaded, attempting to load...")
            if not self.load_book(book_id):
                return None
        
        return self.vector_stores.get(book_id)
    
    def unload_book(self, book_id: str) -> bool:
        """
        Unload a book's vector store from memory.
        
        Args:
            book_id: Book identifier
            
        Returns:
            True if unloaded successfully
        """
        if book_id in self.loaded_books:
            self.loaded_books.remove(book_id)
            if book_id in self.vector_stores:
                del self.vector_stores[book_id]
            logger.info(f"Unloaded book: {book_id}")
            return True
        return False
    
    def add_custom_book(
        self,
        book_id: str,
        name: str,
        display_name: str,
        language: str = "English",
        description: str = ""
    ) -> bool:
        """
        Add a custom book to the available books.
        
        Args:
            book_id: Unique identifier (snake_case recommended)
            name: Short name
            display_name: Full display name
            language: Language of the text
            description: Brief description
            
        Returns:
            True if added successfully
        """
        if book_id in self.books:
            logger.warning(f"Book {book_id} already exists")
            return False
        
        self.books[book_id] = {
            "name": name,
            "display_name": display_name,
            "language": language,
            "description": description
        }
        
        logger.info(f"Added custom book: {book_id} - {display_name}")
        return True
    
    def get_loaded_books(self) -> List[str]:
        """
        Get list of currently loaded book IDs.
        
        Returns:
            List of book IDs
        """
        return self.loaded_books.copy()
    
    def is_book_loaded(self, book_id: str) -> bool:
        """
        Check if a book is currently loaded.
        
        Args:
            book_id: Book identifier
            
        Returns:
            True if loaded
        """
        return book_id in self.loaded_books
    
    def get_book_display_name(self, book_id: str) -> str:
        """
        Get the display name for a book.
        
        Args:
            book_id: Book identifier
            
        Returns:
            Display name or book_id if not found
        """
        book_info = self.books.get(book_id)
        if book_info:
            return book_info.get('display_name', book_info.get('name', book_id))
        return book_id
    
    def migrate_legacy_vector_store(self) -> bool:
        """
        Migrate the legacy vector store (from root) to bhagavad_gita subdirectory.
        
        Returns:
            True if migration successful or not needed
        """
        try:
            legacy_path = get_vector_store_path(None)  # Get root path
            legacy_index = legacy_path / "faiss.index"
            legacy_docs = legacy_path / "documents.pkl"
            
            # Check if legacy files exist
            if not (legacy_index.exists() and legacy_docs.exists()):
                logger.debug("No legacy vector store found, migration not needed")
                return True
            
            # Check if already migrated
            new_path = get_vector_store_path("bhagavad_gita")
            new_index = new_path / "faiss.index"
            new_docs = new_path / "documents.pkl"
            
            if new_index.exists() and new_docs.exists():
                logger.info("Bhagavad Gita vector store already exists, skipping migration")
                return True
            
            # Perform migration
            logger.info("Migrating legacy vector store to bhagavad_gita/")
            import shutil
            shutil.copy2(legacy_index, new_index)
            shutil.copy2(legacy_docs, new_docs)
            
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during migration: {e}", exc_info=True)
            return False

