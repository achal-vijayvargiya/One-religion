"""
PDF text extraction module with metadata preservation.
"""

from typing import List, Dict, Any
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from src.logger import get_logger

logger = get_logger(__name__)


class PDFExtractor:
    """Extract text content from PDF files while preserving metadata."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        logger.debug("PDFExtractor initialized")
    
    def extract(self, pdf_path: str) -> List[Document]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of Document objects with page-level text and metadata
        """
        logger.info(f"Starting PDF extraction: {pdf_path}")
        
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        pdf_size = Path(pdf_path).stat().st_size / (1024 * 1024)  # Size in MB
        logger.debug(f"PDF file size: {pdf_size:.2f} MB")
        
        try:
            # Use LangChain's PyPDFLoader for extraction
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            logger.info(f"Successfully extracted {len(documents)} pages")
            logger.debug(f"Total characters extracted: {sum(len(doc.page_content) for doc in documents)}")
            
            # Enhance metadata with additional information
            for idx, doc in enumerate(documents):
                doc.metadata.update({
                    "source": pdf_path,
                    "page": doc.metadata.get("page", idx),
                    "total_pages": len(documents),
                    "doc_id": Path(pdf_path).stem,
                })
            
            logger.debug("Metadata enhancement complete")
            return documents
            
        except Exception as e:
            logger.error(f"Error during PDF extraction: {str(e)}", exc_info=True)
            raise
    
    def extract_with_structure(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF with additional structural information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing documents and metadata
        """
        logger.info(f"Extracting PDF with structure: {pdf_path}")
        documents = self.extract(pdf_path)
        
        result = {
            "documents": documents,
            "total_pages": len(documents),
            "source": pdf_path,
            "total_chars": sum(len(doc.page_content) for doc in documents),
        }
        
        logger.debug(f"Structure extraction complete: {result['total_pages']} pages, {result['total_chars']} characters")
        return result


def extract_pdf(pdf_path: str) -> List[Document]:
    """
    Convenience function to extract text from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of Document objects
    """
    extractor = PDFExtractor()
    return extractor.extract(pdf_path)

