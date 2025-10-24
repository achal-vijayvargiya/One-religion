# 🕉️ Multi-Religious Text RAG System

A complete **Retrieval-Augmented Generation (RAG)** pipeline for multiple religious texts, featuring semantic chunking, innovative **agentic grouping**, and **side-by-side book comparison**. Chat with the Bhagavad Gita, Bible, Quran, and more simultaneously!

## 🎯 Features

- **📚 Multi-Book Support** (NEW): Query multiple religious texts simultaneously
- **🔄 Side-by-Side Comparison** (NEW): See responses from different books in parallel columns
- **PDF Text Extraction**: Extracts content while preserving metadata and structure
- **Semantic Chunking**: Context-aware text segmentation using LangChain
- **Agentic Grouping**: LLM-powered knowledge cluster creation for better context
- **Vector Search**: FAISS-based similarity search with HuggingFace embeddings
- **Intelligent Q&A**: OpenRouter-powered answer generation with source citations
- **💬 Conversational Mode**: Multi-turn conversations with memory and context
- **🎨 Beautiful Web Interface**: Streamlit UI with intuitive book selection
- **🔌 Extensible**: Easily add custom religious texts

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   PDF File  │────▶│  Extraction  │────▶│   Semantic   │
└─────────────┘     └──────────────┘     │   Chunking   │
                                          └──────┬───────┘
                                                 │
                                                 ▼
                    ┌──────────────┐     ┌──────────────┐
                    │    Vector    │◀────│   Agentic    │
                    │    Store     │     │   Grouping   │
                    │   (FAISS)    │     │  (LLM-based) │
                    └──────┬───────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐     ┌──────────────┐
                    │  Retrieval   │────▶│   Answer     │
                    │    Engine    │     │  Generation  │
                    └──────────────┘     └──────────────┘
```

## 📚 Supported Religious Texts

The system comes pre-configured for these major religious texts:

| Book | Status | Description |
|------|--------|-------------|
| 🕉️ Bhagavad Gita | ✅ Included | Hindu scripture - Krishna and Arjuna's dialogue |
| ✝️ Bible | 📥 Add your own | Christian scripture - Old & New Testament |
| ☪️ Quran | 📥 Add your own | Islamic scripture - Revelations to Prophet Muhammad |
| ➕ Custom Books | 🔌 Extensible | Add any religious text via UI or CLI |

**Each book maintains its own vector store** for independent retrieval and comparison.

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Setup

1. **Clone or navigate to the repository**:
```bash
cd "Bhgwat geeta Guru"
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:

Create a `.env` file in the project root (copy from `env.example`):
```bash
cp env.example .env
```

Edit `.env` and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-sonnet
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=./vector_store
CHUNK_SIZE=800
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

## 🚀 Usage

### Option 1: Streamlit Web Interface (Recommended)

Launch the interactive web application:

```bash
streamlit run app.py
```

The interface provides two main tabs:

1. **📄 Ingest PDF**:
   - Select which book the PDF belongs to (Bhagavad Gita, Bible, Quran, or custom)
   - Upload PDF files
   - Configure agentic grouping
   - View ingestion statistics
   
2. **💬 Chat**:
   - **📚 Select one or multiple books** to query
   - Natural conversational interface
   - Multi-turn conversations with context
   - **🔄 Side-by-side comparison** when multiple books selected
   - View answers with source citations per book
   - Toggle conversation mode on/off
   - Clear chat history

### Option 2: Command Line Interface

Process a PDF via command line:

```bash
# Ingest Bhagavad Gita (default)
python pipeline.py "resources/bhagavad_gita/Bhagavad-gita-As-It-Is.pdf"

# Ingest Bible
python pipeline.py "resources/bible/KJV.pdf" --book-id bible

# Ingest Quran
python pipeline.py "resources/quran/Quran.pdf" --book-id quran

# Add a custom book
python pipeline.py "resources/torah/Torah.pdf" --book-id torah
```

**CLI Options**:
- `--book-id`: Book identifier (default: `bhagavad_gita`)
- `--no-grouping`: Disable agentic grouping (faster but less context-aware)
- `--no-save`: Don't persist the vector store to disk

**Example**:
```bash
# Process Bible with all features
python pipeline.py "resources/bible/NIV.pdf" --book-id bible

# Process Quran without grouping (faster)
python pipeline.py "resources/quran/Quran.pdf" --book-id quran --no-grouping
```

### Option 3: Python API

Use the pipeline programmatically:

```python
from pipeline import RAGPipeline
from src.book_manager import BookManager
from src.multi_book_retrieval import MultiBookRetrieval

# Ingest a PDF for a specific book
pipeline = RAGPipeline(book_id="bible")
stats = pipeline.ingest_pdf(
    pdf_path="resources/bible/KJV.pdf",
    use_grouping=True,
    save_store=True,
)

# Query single book
from src.retrieval_engine import RetrievalEngine
engine = RetrievalEngine(vector_store=pipeline.vector_store, book_id="bible")
result = engine.query("What are the Ten Commandments?")
print(result["answer"])

# Query multiple books simultaneously
book_manager = BookManager()
book_manager.load_book("bhagavad_gita")
book_manager.load_book("bible")

multi_retrieval = MultiBookRetrieval(book_manager)
results = multi_retrieval.query_multiple_books(
    question="What is the path to salvation?",
    book_ids=["bhagavad_gita", "bible"]
)

for book_id, result in results.items():
    print(f"\n{result['book_name']}:")
    print(result["answer"])
```

## 🧩 Project Structure

```
BhgwatGeetaGuru/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management with multi-book support
│   ├── logger.py                # Logging configuration
│   ├── book_manager.py          # Multi-book vector store manager (NEW)
│   ├── multi_book_retrieval.py  # Multi-book query orchestrator (NEW)
│   ├── conversation_manager.py  # Conversation history management
│   ├── pdf_extractor.py         # PDF text extraction
│   ├── semantic_chunker.py      # Semantic chunking logic
│   ├── agentic_grouper.py       # LLM-powered grouping
│   ├── vector_store.py          # FAISS vector operations (book-aware)
│   └── retrieval_engine.py      # Query and answer generation
├── resources/                   # PDF storage by book (NEW structure)
│   ├── bhagavad_gita/
│   │   └── Bhagavad-gita-As-It-Is.pdf
│   ├── bible/
│   │   └── README.md            # Instructions to add Bible PDF
│   └── quran/
│       └── README.md            # Instructions to add Quran PDF
├── vector_store/                # Book-specific vector stores (NEW)
│   ├── bhagavad_gita/
│   │   ├── faiss.index
│   │   └── documents.pkl
│   ├── bible/                   # Created after ingestion
│   └── quran/                   # Created after ingestion
├── logs/                        # Log files (auto-generated)
│   ├── rag_pipeline_*.log       # Main logs
│   └── errors_*.log             # Error logs
├── app.py                       # Streamlit web interface (multi-book UI)
├── pipeline.py                  # Main ingestion pipeline (book-aware)
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
├── README.md                    # This file
└── TROUBLESHOOTING.md           # Troubleshooting guide
```

## 🔧 How It Works

### 1. PDF Extraction
- Uses LangChain's `PyPDFLoader` to extract text page by page
- Preserves metadata (page numbers, document info)

### 2. Semantic Chunking
- Employs `RecursiveCharacterTextSplitter` with intelligent separators
- Creates chunks of ~800 characters with 200-character overlap
- Maintains context boundaries (paragraphs, sentences)

### 3. Agentic Grouping (The Innovation 🌟)
- **What**: LLM analyzes chunks and creates knowledge clusters
- **How**: 
  1. Sends chunk previews to OpenRouter LLM (in batches for large docs)
  2. LLM identifies thematic relationships and boundaries
  3. Groups related chunks into coherent knowledge units
  4. Assigns meaningful titles, themes, and summaries
- **Why**: Better context preservation and more relevant retrieval
- **Batch Processing**: Automatically handles large documents without context limit errors

### 4. Vector Store Creation
- Uses HuggingFace `sentence-transformers` for embeddings
- Builds FAISS index for efficient similarity search
- Stores metadata alongside vectors for rich retrieval

### 5. Retrieval & Answer Generation
- Performs semantic similarity search
- Retrieves top-k most relevant groups/chunks
- Uses OpenRouter LLM to generate contextual answers
- Provides source citations with page numbers
- **NEW**: Conversation history management
- **NEW**: Context-aware query reformulation for follow-ups

### 6. Multi-Book Management (NEW)
- **Separate Vector Stores**: Each book gets its own FAISS index in `vector_store/<book_id>/`
- **Book Manager**: Centralized management of multiple vector stores
- **Parallel Queries**: Query multiple books simultaneously
- **Independent Histories**: Each book maintains separate conversation context
- **Automatic Migration**: Legacy single vector store automatically migrated to `bhagavad_gita/`

## 📖 Multi-Book Usage Examples

### Adding New Books

**Via Streamlit UI:**
1. Go to "Ingest PDF" tab
2. Select the book from dropdown (or choose "Add Custom Book")
3. Upload your PDF
4. Process with or without agentic grouping

**Via CLI:**
```bash
# Add Bible
python pipeline.py resources/bible/KJV.pdf --book-id bible

# Add Quran
python pipeline.py resources/quran/Quran-English.pdf --book-id quran

# Add custom book
python pipeline.py resources/torah/Torah.pdf --book-id torah
```

### Querying Multiple Books

**Single Book Query:**
1. Select one book from the multi-select dropdown
2. Ask your question
3. Get answer with sources from that book

**Multi-Book Comparison:**
1. Select 2+ books (e.g., Bhagavad Gita + Bible)
2. Ask a question like "What is the nature of the soul?"
3. See responses **side-by-side** in separate columns
4. Each book provides its own answer and sources

**Example Questions for Comparison:**
- "What is the path to enlightenment/salvation?"
- "What is the nature of God?"
- "How should one live a righteous life?"
- "What happens after death?"
- "What is the role of faith vs. action?"

### Managing Books

**Sidebar Status:**
- ✅ = Book loaded in memory (fast queries)
- 📥 = Book available on disk (click to load)
- ⭕ = Book not yet ingested

**Actions:**
- "Load All Available Books" - Load all ingested books into memory
- "Clear Chat History" - Reset conversation for all books

## 🎛️ Configuration

All configuration is managed via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `OPENROUTER_MODEL` | Model to use for LLM calls | `anthropic/claude-3-sonnet` |
| `EMBEDDING_MODEL` | HuggingFace model for embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| `VECTOR_STORE_PATH` | Directory for persistent storage | `./vector_store` |
| `CHUNK_SIZE` | Characters per chunk | `800` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `TOP_K_RESULTS` | Results to retrieve per query | `5` |
| `GROUPING_BATCH_SIZE` | Chunks per batch for grouping | `50` |
| `GROUPING_PREVIEW_LENGTH` | Preview length for each chunk | `150` |
| `LOG_DIR` | Directory for log files | `logs` |
| `LOG_LEVEL` | File logging level | `INFO` |
| `CONSOLE_LOG_LEVEL` | Console logging level | `INFO` |

## 📊 Performance Tips

### For Large PDFs (100+ pages):
- Consider disabling agentic grouping for faster processing
- Increase `CHUNK_SIZE` to reduce total chunks
- Use GPU-accelerated FAISS if available

### For Better Accuracy:
- Enable agentic grouping (slower but more context-aware)
- Increase `TOP_K_RESULTS` for more comprehensive answers
- Use more powerful models (e.g., GPT-4)

## 🤝 Supported Models

### LLM (via OpenRouter):
- ✅ **Anthropic Claude** (Recommended: claude-3.5-sonnet)
- ✅ **OpenAI GPT-4/GPT-3.5** (Good alternative)
- ✅ **Meta Llama** (Cost-effective)
- ⚠️ **Google Gemini** (Works, but Gemma models not recommended)
- And many more ([See all models](https://openrouter.ai/models))

**Note:** Some models (like Gemma) don't support system messages. The code handles this automatically, but we recommend Claude or GPT for best results.

📖 **See [MODEL_COMPATIBILITY.md](MODEL_COMPATIBILITY.md) for detailed model guide**

### Embeddings (via HuggingFace):
- `sentence-transformers/all-MiniLM-L6-v2` (default, 384 dims)
- `sentence-transformers/all-mpnet-base-v2` (768 dims, better quality)
- `BAAI/bge-large-en-v1.5` (1024 dims, state-of-the-art)

## 💬 Conversational Mode (NEW!)

Have natural conversations with your documents:

```
You: What is karma yoga?
AI: Karma yoga is the path of selfless action...

You: How does it differ from bhakti yoga?
AI: While karma yoga focuses on action, bhakti yoga emphasizes devotion...

You: Which chapter discusses this?
AI: Karma yoga is primarily discussed in Chapter 3...
```

**Features:**
- 🧠 Remembers previous questions and answers
- 🔄 Understands follow-up questions automatically
- 🎯 Query reformulation for context clarity
- 💬 Modern chat interface
- 🗑️ Clear chat anytime

📖 **See [CONVERSATION_MODE.md](CONVERSATION_MODE.md) for full documentation**

## 📝 Logging

The system includes comprehensive file-based logging:

- **Log Directory**: `logs/` (configurable)
- **Log Files**: 
  - `rag_pipeline_YYYYMMDD.log` - All operations
  - `errors_YYYYMMDD.log` - Errors only
- **Automatic Rotation**: 10MB max, 5 backups
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Quick Start

View logs in real-time:
```bash
tail -f logs/rag_pipeline_20251022.log
```

Find errors:
```bash
grep "ERROR" logs/rag_pipeline_20251022.log
```

📖 **See [LOGGING.md](LOGGING.md) for complete logging guide**

## 🐛 Troubleshooting

### Context Length Error (Error 400)
**Error**: "This endpoint's maximum context length is 131072 tokens..."

**Why it happens in some batches but not others**: The token count varies depending on the actual content length in each batch. Some batches have shorter chunks and succeed, while others with longer chunks exceed the limit.

**Solution**: The system uses batch processing automatically! If you encounter this intermittently:

**Quick Fix** (Create or update `.env` file):
```bash
GROUPING_BATCH_SIZE=20
GROUPING_PREVIEW_LENGTH=100
```

**Or estimate optimal settings**:
```bash
python estimate_tokens.py
```

**Alternative**: Disable agentic grouping in the UI (still works great!)

📖 **See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions**

### Debugging Issues

Enable debug logging in `.env`:
```bash
LOG_LEVEL=DEBUG
CONSOLE_LOG_LEVEL=DEBUG
```

Check logs for detailed information:
```bash
tail -f logs/rag_pipeline_*.log
```

### "OPENROUTER_API_KEY not found"
- Ensure `.env` file exists in the project root
- Verify the API key is correctly set
- Check file permissions

### "No module named 'src'"
- Run commands from the project root directory
- Ensure all files in `src/` are present

### "Developer instruction is not enabled" (Gemma models)
**Error:** Some models don't support system messages

**Solution:** The code now handles this automatically! But for best results:
```bash
# Switch to Claude in .env
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

📖 **See [MODEL_COMPATIBILITY.md](MODEL_COMPATIBILITY.md) for model recommendations**

### JSON Parsing Errors
**Error:** "Failed to parse LLM response as JSON"

**Cause:** Some models (like Gemma) wrap JSON in markdown code blocks

**Solution:** Now fixed automatically! The parser handles:
- ✅ Markdown code fences (` ```json`)
- ✅ Trailing commas
- ✅ Extra whitespace

If you still get errors, try:
```bash
OPENROUTER_MODEL=anthropic/claude-3-sonnet  # Better JSON output
```

📖 **See [JSON_PARSING_FIX.md](JSON_PARSING_FIX.md) for technical details**

### Windows Encoding Errors
**Error:** `'charmap' codec can't encode character '\u2713'`

**Cause:** Windows console uses cp1252 encoding which doesn't support Unicode

**Solution:** Fixed automatically! The code now:
- ✅ Uses ASCII-safe characters in console output
- ✅ Sets UTF-8 encoding when possible
- ✅ File logs still support all Unicode

📖 **See [WINDOWS_ENCODING_FIX.md](WINDOWS_ENCODING_FIX.md) for details**

### Slow ingestion
- Agentic grouping requires multiple LLM calls (batch processing)
- Use `--no-grouping` flag for faster processing
- Check your internet connection

### Poor answer quality
- Try increasing `TOP_K_RESULTS`
- Enable agentic grouping if disabled
- Use a more powerful model

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [OpenRouter](https://openrouter.ai/)
- Embeddings by [Sentence Transformers](https://www.sbert.net/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
- UI with [Streamlit](https://streamlit.io/)

---

**Made with ❤️ for exploring ancient wisdom through modern AI**

