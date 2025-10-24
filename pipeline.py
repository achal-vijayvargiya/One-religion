"""
Main ingestion pipeline orchestrating the RAG workflow.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from tqdm import tqdm

from src.pdf_extractor import PDFExtractor
from src.semantic_chunker import SemanticChunker
from src.agentic_grouper import AgenticGrouper
from src.vector_store import VectorStoreManager
from src.config import validate_config
from src.logger import setup_logging, get_logger

# Fix Windows encoding for emojis (optional - logging already handles this)
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass  # Not critical

# Initialize logging
setup_logging()
logger = get_logger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for PDF ingestion."""
    
    def __init__(self, book_id: Optional[str] = None):
        """
        Initialize the pipeline components.
        
        Args:
            book_id: Optional book identifier for book-specific storage
        """
        logger.info(f"Initializing RAG Pipeline (book_id: {book_id})")
        self.pdf_extractor = PDFExtractor()
        self.semantic_chunker = SemanticChunker()
        self.agentic_grouper = AgenticGrouper()
        self.vector_store = VectorStoreManager(book_id=book_id)
        self.book_id = book_id
        logger.info("RAG Pipeline initialized successfully")
    
    def ingest_pdf(
        self,
        pdf_path: str,
        use_grouping: bool = True,
        save_store: bool = True,
    ) -> dict:
        """
        Ingest a PDF through the complete pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            use_grouping: Whether to use agentic grouping
            save_store: Whether to save the vector store to disk
            
        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Starting PDF ingestion: {pdf_path}")
        logger.info(f"Options: use_grouping={use_grouping}, save_store={save_store}")
        
        print(f"\n{'='*60}")
        print(f"RAG Pipeline - PDF Ingestion")
        print(f"{'='*60}\n")
        
        # Step 1: Extract PDF
        print("Step 1: Extracting PDF content...")
        logger.info("Step 1: PDF Extraction")
        documents = self.pdf_extractor.extract(pdf_path)
        print(f"   [OK] Extracted {len(documents)} pages")
        
        # Step 2: Semantic Chunking
        print("\nStep 2: Performing semantic chunking...")
        logger.info("Step 2: Semantic Chunking")
        chunks = self.semantic_chunker.chunk_documents(documents)
        print(f"   [OK] Created {len(chunks)} semantic chunks")
        
        # Step 3: Agentic Grouping (optional)
        if use_grouping:
            print("\nStep 3: Agentic grouping (LLM-powered)...")
            logger.info("Step 3: Agentic Grouping (enabled)")
            groups = self.agentic_grouper.group_chunks(chunks)
            print(f"   [OK] Created {len(groups)} knowledge groups")
            
            # Convert groups to documents
            final_documents = self.agentic_grouper.create_group_documents(groups)
            print(f"   [OK] Prepared {len(final_documents)} documents for indexing")
            logger.info(f"Created {len(final_documents)} grouped documents")
        else:
            print("\nStep 3: Skipping agentic grouping")
            logger.info("Step 3: Agentic Grouping (skipped)")
            final_documents = chunks
        
        # Step 4: Create Vector Store
        print("\nStep 4: Creating vector embeddings...")
        logger.info("Step 4: Vector Store Creation")
        self.vector_store.create_index(final_documents)
        print(f"   [OK] Indexed {len(final_documents)} documents")
        
        # Step 5: Save Vector Store
        if save_store:
            print("\nStep 5: Saving vector store...")
            logger.info("Step 5: Saving Vector Store")
            self.vector_store.save()
            print("   [OK] Vector store saved successfully")
        else:
            logger.info("Step 5: Vector Store Save (skipped)")
        
        print(f"\n{'='*60}")
        print("[SUCCESS] Ingestion complete!")
        print(f"{'='*60}\n")
        
        logger.info(f"Pipeline ingestion completed successfully: {len(final_documents)} documents indexed")
        
        return {
            "pdf_path": pdf_path,
            "pages": len(documents),
            "chunks": len(chunks),
            "groups": len(groups) if use_grouping else 0,
            "indexed_documents": len(final_documents),
            "use_grouping": use_grouping,
        }


def main():
    """CLI entry point for the pipeline."""
    logger.info("=" * 80)
    logger.info("RAG Pipeline CLI started")
    logger.info("=" * 80)
    
    parser = argparse.ArgumentParser(
        description="RAG Pipeline - Ingest PDF documents for question answering"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to the PDF file to ingest",
    )
    parser.add_argument(
        "--book-id",
        type=str,
        default="bhagavad_gita",
        help="Book identifier (e.g., 'bhagavad_gita', 'bible', 'quran'). Default: bhagavad_gita",
    )
    parser.add_argument(
        "--no-grouping",
        action="store_true",
        help="Disable agentic grouping (faster but less context-aware)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save the vector store to disk",
    )
    
    args = parser.parse_args()
    logger.info(f"Command line arguments: {args}")
    
    # Validate PDF path
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return 1
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        print(f"[ERROR] Configuration Error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from env.example)")
        print("2. Set your OPENROUTER_API_KEY")
        return 1
    
    # Run pipeline
    try:
        pipeline = RAGPipeline(book_id=args.book_id)
        print(f"\n📖 Processing for book: {args.book_id}")
        stats = pipeline.ingest_pdf(
            pdf_path=str(pdf_path),
            use_grouping=not args.no_grouping,
            save_store=not args.no_save,
        )
        
        print("\n📊 Ingestion Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        logger.info("Pipeline completed successfully")
        logger.info(f"Statistics: {stats}")
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

