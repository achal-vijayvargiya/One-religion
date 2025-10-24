"""
Semantic chunking module for context-aware text segmentation.
"""

from typing import List, Optional
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)


class SemanticChunker:
    """Perform semantic chunking on documents."""
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        """
        Initialize the semantic chunker.
        
        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
        """
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        logger.info(f"Initializing SemanticChunker: chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}")
        
        # RecursiveCharacterTextSplitter provides semantic-aware splitting
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence ends
                "! ",
                "? ",
                "; ",
                ", ",
                " ",     # Words
                "",      # Characters
            ],
            keep_separator=True,
        )
        logger.debug("RecursiveCharacterTextSplitter configured")
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into semantic chunks.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents with preserved metadata
        """
        logger.info(f"Starting semantic chunking for {len(documents)} documents")
        chunks = []
        
        for doc_idx, doc in enumerate(documents):
            # Split the document
            doc_chunks = self.splitter.split_documents([doc])
            logger.debug(f"Document {doc_idx + 1}/{len(documents)}: Created {len(doc_chunks)} chunks")
            
            # Add chunk-specific metadata
            for idx, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "chunk_id": f"{chunk.metadata.get('doc_id', 'doc')}_{chunk.metadata.get('page', 0)}_{idx}",
                    "chunk_index": idx,
                    "chunk_size": len(chunk.page_content),
                })
                chunks.append(chunk)
        
        logger.info(f"Chunking complete: {len(chunks)} total chunks created")
        logger.debug(f"Average chunk size: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} characters")
        return chunks
    
    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> List[Document]:
        """
        Chunk raw text into documents.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunked documents
        """
        logger.debug(f"Chunking raw text: {len(text)} characters")
        base_metadata = metadata or {}
        
        # Create a document from the text
        doc = Document(page_content=text, metadata=base_metadata)
        
        # Chunk it
        chunks = self.splitter.split_documents([doc])
        logger.debug(f"Text chunked into {len(chunks)} pieces")
        
        # Add chunk metadata
        for idx, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": f"chunk_{idx}",
                "chunk_index": idx,
                "chunk_size": len(chunk.page_content),
            })
        
        return chunks


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Convenience function to chunk documents.
    
    Args:
        documents: Documents to chunk
        
    Returns:
        List of chunked documents
    """
    chunker = SemanticChunker()
    return chunker.chunk_documents(documents)

