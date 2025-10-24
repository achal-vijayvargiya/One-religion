"""
Example usage script demonstrating the RAG pipeline API.

This script shows how to use the RAG pipeline programmatically
without the Streamlit UI or CLI.
"""

from pathlib import Path
from pipeline import RAGPipeline
from src.retrieval_engine import RetrievalEngine
from src.vector_store import VectorStoreManager


def example_full_pipeline():
    """Example: Complete pipeline from PDF to Q&A."""
    print("\n" + "="*60)
    print("Example 1: Full Pipeline (Ingest + Query)")
    print("="*60 + "\n")
    
    # Define your PDF path
    pdf_path = "resources/Bhagavad-gita-As-It-Is.pdf"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  PDF not found: {pdf_path}")
        print("Please provide a valid PDF path")
        return
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Ingest the PDF
    print("Step 1: Ingesting PDF...")
    stats = pipeline.ingest_pdf(
        pdf_path=pdf_path,
        use_grouping=True,  # Enable agentic grouping
        save_store=True,    # Save to disk
    )
    
    print(f"\n📊 Ingestion complete:")
    print(f"   - Pages: {stats['pages']}")
    print(f"   - Chunks: {stats['chunks']}")
    print(f"   - Groups: {stats['groups']}")
    print(f"   - Indexed: {stats['indexed_documents']}")
    
    # Create retrieval engine
    print("\nStep 2: Creating retrieval engine...")
    engine = RetrievalEngine(vector_store=pipeline.vector_store)
    
    # Ask questions
    questions = [
        "What is the main teaching of the Bhagavad Gita?",
        "Who are the main characters?",
        "What is karma yoga?",
    ]
    
    print("\nStep 3: Asking questions...\n")
    
    for question in questions:
        print(f"❓ Question: {question}")
        result = engine.query(question, k=3)
        print(f"💡 Answer:\n{result['answer']}\n")
        print(f"📚 Used {result['num_sources']} sources")
        print("-" * 60 + "\n")


def example_load_existing():
    """Example: Load existing vector store and query."""
    print("\n" + "="*60)
    print("Example 2: Load Existing Vector Store")
    print("="*60 + "\n")
    
    # Load existing vector store
    vector_store = VectorStoreManager()
    
    if not vector_store.load():
        print("❌ No existing vector store found.")
        print("   Run Example 1 first to create one.")
        return
    
    print("✅ Vector store loaded successfully!\n")
    
    # Create retrieval engine
    engine = RetrievalEngine(vector_store=vector_store)
    
    # Interactive query
    question = "What does Krishna teach about duty?"
    print(f"❓ Question: {question}\n")
    
    result = engine.query(question, k=5)
    
    print(f"💡 Answer:\n{result['answer']}\n")
    
    print(f"📚 Sources ({result['num_sources']}):")
    for idx, source in enumerate(result['sources'], 1):
        print(f"\n{idx}. {source.get('title', 'Source')} (Pages: {source['pages']})")
        print(f"   Distance: {source['distance']:.4f}")
        if source.get('theme'):
            print(f"   Theme: {source['theme']}")


def example_retrieval_only():
    """Example: Retrieve documents without generating answers."""
    print("\n" + "="*60)
    print("Example 3: Retrieval Only (No Answer Generation)")
    print("="*60 + "\n")
    
    # Load vector store
    vector_store = VectorStoreManager()
    
    if not vector_store.load():
        print("❌ No existing vector store found.")
        return
    
    # Create engine
    engine = RetrievalEngine(vector_store=vector_store)
    
    # Retrieve documents
    query = "meditation and self-realization"
    print(f"🔍 Searching for: '{query}'\n")
    
    documents = engine.retrieve_only(query, k=3)
    
    print(f"Found {len(documents)} relevant documents:\n")
    
    for idx, doc in enumerate(documents, 1):
        print(f"{'='*60}")
        print(f"Document {idx}")
        print(f"{'='*60}")
        print(f"Distance: {doc['distance']:.4f}")
        print(f"Type: {doc['metadata'].get('type', 'chunk')}")
        if doc['metadata'].get('title'):
            print(f"Title: {doc['metadata']['title']}")
        print(f"\nContent Preview:")
        print(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
        print("\n")


def example_custom_chunking():
    """Example: Use custom chunking parameters."""
    print("\n" + "="*60)
    print("Example 4: Custom Chunking Parameters")
    print("="*60 + "\n")
    
    from src.pdf_extractor import PDFExtractor
    from src.semantic_chunker import SemanticChunker
    
    pdf_path = "resources/Bhagavad-gita-As-It-Is.pdf"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  PDF not found: {pdf_path}")
        return
    
    # Extract PDF
    extractor = PDFExtractor()
    documents = extractor.extract(pdf_path)
    
    print(f"Extracted {len(documents)} pages\n")
    
    # Custom chunking - smaller chunks
    chunker_small = SemanticChunker(chunk_size=400, chunk_overlap=100)
    chunks_small = chunker_small.chunk_documents(documents)
    
    # Custom chunking - larger chunks
    chunker_large = SemanticChunker(chunk_size=1500, chunk_overlap=300)
    chunks_large = chunker_large.chunk_documents(documents)
    
    print(f"Small chunks (400 chars): {len(chunks_small)} chunks")
    print(f"Large chunks (1500 chars): {len(chunks_large)} chunks")
    print(f"\nTrade-off: More chunks = finer granularity but more processing")


def example_without_grouping():
    """Example: Process without agentic grouping for speed."""
    print("\n" + "="*60)
    print("Example 5: Fast Processing (No Agentic Grouping)")
    print("="*60 + "\n")
    
    pdf_path = "resources/Bhagavad-gita-As-It-Is.pdf"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  PDF not found: {pdf_path}")
        return
    
    import time
    
    pipeline = RAGPipeline()
    
    start_time = time.time()
    
    stats = pipeline.ingest_pdf(
        pdf_path=pdf_path,
        use_grouping=False,  # Disable grouping for speed
        save_store=False,
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n⏱️  Processing time: {elapsed:.2f} seconds")
    print(f"📊 Chunks processed: {stats['chunks']}")
    print(f"💡 Tip: Agentic grouping is slower but provides better context")


def main():
    """Run example demonstrations."""
    print("\n" + "="*60)
    print("RAG Pipeline - Example Usage")
    print("="*60)
    
    examples = {
        "1": ("Full Pipeline (Ingest + Query)", example_full_pipeline),
        "2": ("Load Existing Vector Store", example_load_existing),
        "3": ("Retrieval Only", example_retrieval_only),
        "4": ("Custom Chunking", example_custom_chunking),
        "5": ("Fast Processing (No Grouping)", example_without_grouping),
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n" + "="*60)
    
    choice = input("\nSelect an example (1-5) or 'all' to run all: ").strip()
    
    if choice.lower() == 'all':
        for _, func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"❌ Error: {e}\n")
    elif choice in examples:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice. Please run again and select 1-5 or 'all'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

