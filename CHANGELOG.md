# Changelog

All notable changes to the Bhagavad Gita RAG System project.

## [Unreleased] - 2025-10-22

### Added - File-Based Logging System

#### Core Features
- **Comprehensive file-based logging** throughout the entire application
- **Automatic log rotation** (10MB max file size, 5 backup files)
- **Dual log files**: 
  - Main log (`rag_pipeline_YYYYMMDD.log`) for all operations
  - Error log (`errors_YYYYMMDD.log`) for errors only
- **Configurable log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Structured log format** with timestamps, module names, function names, and line numbers

#### New Files
- `src/logger.py` - Centralized logging configuration module
- `LOGGING.md` - Complete logging guide and documentation
- `logs/` directory - Auto-generated log storage (gitignored)

#### Updated Files
- `src/config.py` - Added logging configuration options
- `src/pdf_extractor.py` - Integrated logging
- `src/semantic_chunker.py` - Integrated logging
- `src/agentic_grouper.py` - Integrated logging
- `src/vector_store.py` - Integrated logging
- `src/retrieval_engine.py` - Integrated logging
- `pipeline.py` - Integrated logging
- `app.py` - Integrated logging with Streamlit
- `README.md` - Added logging section and updated project structure
- `env.example` - Added logging configuration variables
- `.gitignore` - Added logs directory

#### Configuration Options

New environment variables in `.env`:

```bash
LOG_DIR=logs                    # Log directory location
LOG_LEVEL=INFO                  # File logging level
CONSOLE_LOG_LEVEL=INFO          # Console logging level
LOG_MAX_BYTES=10485760          # Max file size before rotation (10MB)
LOG_BACKUP_COUNT=5              # Number of backup files to keep
```

#### What Gets Logged

**PDF Extraction:**
- File path, size, and extraction progress
- Page counts and character counts
- Extraction errors and exceptions

**Semantic Chunking:**
- Document processing progress
- Chunk creation statistics
- Average chunk sizes

**Agentic Grouping:**
- Batch processing progress
- LLM API calls and responses
- Group creation details
- Error handling and fallback scenarios

**Vector Store:**
- Model loading and initialization
- Index creation and statistics
- Search operations and results
- Save/load operations

**Retrieval Engine:**
- User queries and processing
- Document retrieval statistics
- Answer generation success/failure
- Source citation information

**Pipeline Operations:**
- Overall workflow progress
- Step-by-step execution
- Configuration validation
- Statistics and metrics

#### Log Format

```
2025-10-22 14:30:45 | INFO     | src.pdf_extractor | extract:31 | Starting PDF extraction: bhagavad-gita.pdf
```

Format: `timestamp | level | module | function:line | message`

#### Benefits

1. **Debugging** - Detailed trace of all operations
2. **Monitoring** - Track system behavior in production
3. **Troubleshooting** - Quickly identify and resolve issues
4. **Auditing** - Complete record of all operations
5. **Performance Analysis** - Identify bottlenecks and slow operations

#### Usage Examples

**View real-time logs:**
```bash
tail -f logs/rag_pipeline_20251022.log
```

**Search for errors:**
```bash
grep "ERROR" logs/rag_pipeline_20251022.log
```

**Enable debug mode:**
```bash
# In .env
LOG_LEVEL=DEBUG
CONSOLE_LOG_LEVEL=DEBUG
```

### Previous Changes

#### [v1.1.0] - Context Length Error Fix
- Implemented batch processing for agentic grouping
- Added automatic handling of large documents
- Created `TROUBLESHOOTING.md` guide
- Optimized prompts to reduce token usage

#### [v1.0.0] - Initial Release
- PDF extraction with LangChain
- Semantic chunking with configurable parameters
- Agentic grouping with LLM-powered knowledge clustering
- FAISS vector store with HuggingFace embeddings
- Intelligent Q&A with OpenRouter integration
- Streamlit web interface
- Command-line interface

## Notes

For detailed logging documentation, see [LOGGING.md](LOGGING.md).
For troubleshooting help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

