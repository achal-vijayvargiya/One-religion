"""
Vector store management using FAISS and HuggingFace embeddings.
"""

import pickle
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
from src.config import get_settings, get_vector_store_path
from src.logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """Manage FAISS vector store with HuggingFace embeddings."""
    
    def __init__(self, embedding_model: Optional[str] = None, book_id: Optional[str] = None):
        """
        Initialize the vector store manager.
        
        Args:
            embedding_model: HuggingFace model name for embeddings
            book_id: Optional book identifier for book-specific storage
        """
        settings = get_settings()
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.book_id = book_id
        
        logger.info(f"Initializing VectorStoreManager with model: {self.embedding_model_name}, book_id: {book_id}")
        
        # Initialize embedding model lazily to avoid device issues during startup
        self.embedding_model = None
        self.embedding_dim = None
        
        # FAISS index and metadata storage
        self.index: Optional[faiss.Index] = None
        self.documents: List[Document] = []
        self.metadata: List[Dict[str, Any]] = []
    
    def _ensure_embedding_model(self):
        """Ensure the embedding model is loaded (lazy loading)."""
        if self.embedding_model is None:
            print(f"Loading embedding model: {self.embedding_model_name}")
            try:
                # Try to load with CPU first to avoid device issues
                self.embedding_model = SentenceTransformer(self.embedding_model_name, device='cpu')
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            except Exception as e:
                logger.warning(f"Failed to load model with CPU device: {e}")
                try:
                    # Fallback: try without specifying device
                    self.embedding_model = SentenceTransformer(self.embedding_model_name)
                    self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                except Exception as e2:
                    logger.error(f"Failed to load embedding model: {e2}")
                    raise RuntimeError(f"Could not load embedding model {self.embedding_model_name}: {e2}")
            
            logger.info(f"Embedding model loaded successfully (dimension: {self.embedding_dim})")
    
    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        self._ensure_embedding_model()
        logger.debug(f"Creating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        logger.debug(f"Embeddings created: shape {embeddings.shape}")
        return embeddings
    
    def create_index(self, documents: List[Document]) -> None:
        """
        Create a FAISS index from documents.
        
        Args:
            documents: List of documents to index
        """
        if not documents:
            logger.error("Attempted to create index from empty document list")
            raise ValueError("Cannot create index from empty document list")
        
        logger.info(f"Creating FAISS index for {len(documents)} documents")
        print(f"Creating embeddings for {len(documents)} documents...")
        
        # Extract text content
        texts = [doc.page_content for doc in documents]
        total_chars = sum(len(t) for t in texts)
        logger.debug(f"Total text length: {total_chars} characters")
        
        # Create embeddings
        embeddings = self._embed_texts(texts)
        
        # Create FAISS index
        # Using IndexFlatL2 for exact search (good for small to medium datasets)
        logger.debug(f"Creating FAISS IndexFlatL2 with dimension {self.embedding_dim}")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings.astype(np.float32))
        
        # Store documents and metadata
        self.documents = documents
        self.metadata = [doc.metadata for doc in documents]
        
        logger.info(f"Index created successfully: {self.index.ntotal} vectors indexed")
        print(f"[OK] Index created with {self.index.ntotal} vectors")
    
    def search(
        self,
        query: str,
        k: int = 5,
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of (document, distance) tuples
        """
        if self.index is None:
            logger.error("Search attempted on uninitialized index")
            raise RuntimeError("Index not created. Call create_index() first.")
        
        logger.debug(f"Searching for query: '{query[:50]}...' (k={k})")
        
        # Embed the query
        query_embedding = self._embed_texts([query])
        
        # Search
        distances, indices = self.index.search(
            query_embedding.astype(np.float32),
            k,
        )
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        
        logger.info(f"Search completed: {len(results)} results found")
        logger.debug(f"Result distances: {[f'{d:.4f}' for _, d in results]}")
        return results
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save the vector store to disk.
        
        Args:
            path: Directory path to save to (defaults to config with book_id)
        """
        if self.index is None:
            logger.error("Save attempted on uninitialized index")
            raise RuntimeError("No index to save. Create an index first.")
        
        save_path = Path(path) if path else get_vector_store_path(self.book_id)
        save_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving vector store to {save_path} (book_id: {self.book_id})")
        
        # Save FAISS index
        index_file = save_path / "faiss.index"
        faiss.write_index(self.index, str(index_file))
        logger.debug(f"FAISS index saved: {index_file}")
        
        # Save documents and metadata
        data_file = save_path / "documents.pkl"
        with open(data_file, "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata,
                "embedding_model": self.embedding_model_name,
                "book_id": self.book_id,
            }, f)
        
        file_size = data_file.stat().st_size / (1024 * 1024)  # MB
        logger.debug(f"Documents saved: {data_file} ({file_size:.2f} MB)")
        logger.info(f"Vector store saved successfully: {self.index.ntotal} vectors, {len(self.documents)} documents")
        print(f"[OK] Vector store saved to {save_path}")
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Load a vector store from disk.
        
        Args:
            path: Directory path to load from (defaults to config with book_id)
            
        Returns:
            True if successful, False otherwise
        """
        load_path = Path(path) if path else get_vector_store_path(self.book_id)
        
        index_file = load_path / "faiss.index"
        data_file = load_path / "documents.pkl"
        
        logger.info(f"Attempting to load vector store from {load_path} (book_id: {self.book_id})")
        
        if not index_file.exists() or not data_file.exists():
            logger.warning(f"Vector store files not found at {load_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            logger.debug(f"FAISS index loaded: {self.index.ntotal} vectors")
            
            # Load documents and metadata
            with open(data_file, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                stored_model = data.get("embedding_model", self.embedding_model_name)
                stored_book_id = data.get("book_id", None)
                
                if stored_model != self.embedding_model_name:
                    logger.warning(f"Model mismatch - Stored: {stored_model}, Current: {self.embedding_model_name}")
                    print(f"[WARNING] Stored model ({stored_model}) differs from current ({self.embedding_model_name})")
                
                if stored_book_id and stored_book_id != self.book_id:
                    logger.warning(f"Book ID mismatch - Stored: {stored_book_id}, Current: {self.book_id}")
            
            logger.info(f"Vector store loaded successfully: {self.index.ntotal} vectors, {len(self.documents)} documents")
            print(f"[OK] Vector store loaded from {load_path} ({self.index.ntotal} vectors)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}", exc_info=True)
            return False
    
    def is_empty(self) -> bool:
        """Check if the vector store is empty."""
        return self.index is None or self.index.ntotal == 0


class VectorStore:
    """Simplified interface for vector store operations."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.manager = VectorStoreManager()
    
    def index_documents(self, documents: List[Document]) -> None:
        """Index documents."""
        self.manager.create_index(documents)
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for documents."""
        return self.manager.search(query, k)
    
    def save(self) -> None:
        """Save to disk."""
        self.manager.save()
    
    def load(self) -> bool:
        """Load from disk."""
        return self.manager.load()

