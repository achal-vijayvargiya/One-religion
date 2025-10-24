# Logging Guide

The RAG Pipeline includes comprehensive file-based logging to help you debug issues and monitor system behavior.

## Overview

All operations are logged to files with rotation support, configurable log levels, and structured formatting.

## Log Files

Logs are stored in the `logs/` directory (configurable via `.env`):

```
logs/
├── rag_pipeline_20251022.log  # All logs (INFO and above)
├── errors_20251022.log         # Errors only (ERROR and above)
├── rag_pipeline_20251022.log.1  # Rotated backups
└── errors_20251022.log.1
```

### Log File Types

1. **Main Log** (`rag_pipeline_YYYYMMDD.log`)
   - Contains all log levels (based on `LOG_LEVEL` setting)
   - Includes INFO, WARNING, ERROR, and DEBUG messages
   - Automatically rotates when size exceeds 10MB
   - Keeps 5 backup files by default

2. **Error Log** (`errors_YYYYMMDD.log`)
   - Contains only ERROR and CRITICAL messages
   - Useful for quickly identifying failures
   - Separate file for easy error tracking

## Configuration

Configure logging in your `.env` file:

```bash
# Logging Configuration
LOG_DIR=logs                    # Directory for log files
LOG_LEVEL=INFO                  # File log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
CONSOLE_LOG_LEVEL=INFO          # Console log level (can be different from file)
LOG_MAX_BYTES=10485760          # Max file size before rotation (10MB)
LOG_BACKUP_COUNT=5              # Number of backup files to keep
```

### Log Levels

Choose the appropriate log level for your needs:

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed diagnostic information | Development, debugging issues |
| `INFO` | General informational messages | Production monitoring |
| `WARNING` | Warning messages (non-critical) | Issues that don't stop execution |
| `ERROR` | Error messages | Failures and exceptions |
| `CRITICAL` | Critical failures | Severe errors requiring immediate attention |

### Recommended Settings

**Development:**
```bash
LOG_LEVEL=DEBUG
CONSOLE_LOG_LEVEL=INFO
```

**Production:**
```bash
LOG_LEVEL=INFO
CONSOLE_LOG_LEVEL=WARNING
```

**Troubleshooting:**
```bash
LOG_LEVEL=DEBUG
CONSOLE_LOG_LEVEL=DEBUG
```

## Log Format

Logs use a structured format for easy parsing and analysis:

```
2025-10-22 14:30:45 | INFO     | src.pdf_extractor | extract:31 | Starting PDF extraction: bhagavad-gita.pdf
2025-10-22 14:30:46 | INFO     | src.pdf_extractor | extract:45 | Successfully extracted 200 pages
2025-10-22 14:30:46 | DEBUG    | src.pdf_extractor | extract:46 | Total characters extracted: 458392
```

**Format breakdown:**
- `2025-10-22 14:30:45`: Timestamp
- `INFO`: Log level
- `src.pdf_extractor`: Module name
- `extract:31`: Function name and line number
- `Starting PDF extraction: bhagavad-gita.pdf`: Log message

## What Gets Logged

### PDF Extraction
- File path and size
- Number of pages extracted
- Character counts
- Errors during extraction

### Semantic Chunking
- Number of documents chunked
- Chunk counts and sizes
- Average chunk size

### Agentic Grouping
- Batch processing progress
- LLM API calls and responses
- Group creation details
- Batch failures and fallbacks

### Vector Store
- Model loading
- Index creation and size
- Search queries and results
- Save/load operations

### Retrieval & QA
- User queries
- Retrieved document counts
- LLM response generation
- Answer generation success/failure

### Pipeline Operations
- Overall workflow progress
- Step-by-step execution
- Statistics and metrics
- Configuration validation

## Example Log Output

### Successful Ingestion

```
2025-10-22 14:30:45 | INFO     | __main__ | main:119 | ================================================================================
2025-10-22 14:30:45 | INFO     | __main__ | main:120 | RAG Pipeline CLI started
2025-10-22 14:30:45 | INFO     | __main__ | main:121 | ================================================================================
2025-10-22 14:30:45 | INFO     | __main__ | __init__:27 | Initializing RAG Pipeline
2025-10-22 14:30:45 | INFO     | src.pdf_extractor | __init__:19 | PDFExtractor initialized
2025-10-22 14:30:46 | INFO     | src.semantic_chunker | __init__:33 | Initializing SemanticChunker: chunk_size=800, chunk_overlap=200
2025-10-22 14:30:46 | INFO     | src.agentic_grouper | __init__:26 | Initializing AgenticGrouper
2025-10-22 14:30:47 | INFO     | src.vector_store | __init__:31 | Initializing VectorStoreManager with model: sentence-transformers/all-MiniLM-L6-v2
2025-10-22 14:30:50 | INFO     | src.vector_store | __init__:38 | Embedding model loaded successfully (dimension: 384)
2025-10-22 14:30:50 | INFO     | __main__ | __init__:32 | RAG Pipeline initialized successfully
2025-10-22 14:30:50 | INFO     | __main__ | ingest_pdf:51 | Starting PDF ingestion: bhagavad-gita.pdf
2025-10-22 14:30:50 | INFO     | __main__ | ingest_pdf:52 | Options: use_grouping=True, save_store=True
2025-10-22 14:30:50 | INFO     | __main__ | ingest_pdf:60 | Step 1: PDF Extraction
2025-10-22 14:30:50 | INFO     | src.pdf_extractor | extract:31 | Starting PDF extraction: bhagavad-gita.pdf
2025-10-22 14:30:52 | INFO     | src.pdf_extractor | extract:45 | Successfully extracted 200 pages
2025-10-22 14:30:52 | INFO     | __main__ | ingest_pdf:66 | Step 2: Semantic Chunking
2025-10-22 14:30:52 | INFO     | src.semantic_chunker | chunk_documents:65 | Starting semantic chunking for 200 documents
2025-10-22 14:30:55 | INFO     | src.semantic_chunker | chunk_documents:82 | Chunking complete: 450 total chunks created
2025-10-22 14:30:55 | INFO     | __main__ | ingest_pdf:73 | Step 3: Agentic Grouping (enabled)
2025-10-22 14:30:55 | INFO     | src.agentic_grouper | group_chunks:236 | Starting chunk grouping: 450 chunks total
2025-10-22 14:30:55 | INFO     | src.agentic_grouper | group_chunks:246 | Processing 450 chunks in 9 batches of 50
2025-10-22 14:31:05 | INFO     | src.agentic_grouper | group_chunks:281 | Chunk grouping complete: 65 total groups created from 450 chunks
2025-10-22 14:31:05 | INFO     | __main__ | ingest_pdf:88 | Step 4: Vector Store Creation
2025-10-22 14:31:05 | INFO     | src.vector_store | create_index:75 | Creating FAISS index for 65 documents
2025-10-22 14:31:12 | INFO     | src.vector_store | create_index:96 | Index created successfully: 65 vectors indexed
2025-10-22 14:31:12 | INFO     | __main__ | ingest_pdf:95 | Step 5: Saving Vector Store
2025-10-22 14:31:12 | INFO     | src.vector_store | save:153 | Saving vector store to ./vector_store
2025-10-22 14:31:12 | INFO     | src.vector_store | save:171 | Vector store saved successfully: 65 vectors, 65 documents
2025-10-22 14:31:12 | INFO     | __main__ | ingest_pdf:105 | Pipeline ingestion completed successfully: 65 documents indexed
2025-10-22 14:31:12 | INFO     | __main__ | main:176 | Pipeline completed successfully
```

### Error Logging

```
2025-10-22 14:35:20 | ERROR    | src.agentic_grouper | _call_llm:124 | Error calling OpenRouter: Error code: 400 - ...
Traceback (most recent call last):
  File "src/agentic_grouper.py", line 108, in _call_llm
    response = self.client.chat.completions.create(
  ...
RuntimeError: Error calling OpenRouter: ...
```

## Viewing Logs

### Real-time Monitoring

Monitor logs in real-time using `tail`:

```bash
# Watch all logs
tail -f logs/rag_pipeline_20251022.log

# Watch errors only
tail -f logs/errors_20251022.log

# Watch with color highlighting (if available)
tail -f logs/rag_pipeline_20251022.log | ccze -A
```

### Searching Logs

Find specific information in logs:

```bash
# Find all errors
grep "ERROR" logs/rag_pipeline_20251022.log

# Find logs related to PDF extraction
grep "pdf_extractor" logs/rag_pipeline_20251022.log

# Find logs for a specific function
grep "group_chunks" logs/rag_pipeline_20251022.log

# Count occurrences
grep -c "LLM response received" logs/rag_pipeline_20251022.log
```

### Analyzing Logs

Common analysis tasks:

```bash
# Count errors by type
grep "ERROR" logs/rag_pipeline_20251022.log | cut -d'|' -f3 | sort | uniq -c

# Find slowest operations (if timing info exists)
grep "completed" logs/rag_pipeline_20251022.log

# Extract all user queries
grep "Processing query" logs/rag_pipeline_20251022.log | cut -d':' -f4-
```

## Log Rotation

Logs automatically rotate to prevent unlimited disk usage:

- **Max Size**: 10MB per file (configurable)
- **Backups**: 5 files kept (configurable)
- **Naming**: `filename.log.1`, `filename.log.2`, etc.
- **Oldest**: Deleted when backup count exceeded

### Manual Rotation

To manually rotate logs:

```bash
# Archive current logs
mkdir -p logs/archive/2025-10
mv logs/*.log logs/archive/2025-10/

# Logs will be recreated automatically
```

## Troubleshooting with Logs

### Common Issues

**1. No log files created**
- Check `LOG_DIR` permissions
- Verify `.env` configuration is loaded
- Check for initialization errors

**2. Logs not being written**
- Verify log level is appropriate
- Check disk space
- Ensure application has write permissions

**3. Too many logs (disk space)**
- Reduce `LOG_LEVEL` to `WARNING` or `ERROR`
- Decrease `LOG_BACKUP_COUNT`
- Decrease `LOG_MAX_BYTES`
- Set up log archival/cleanup

**4. Can't find specific information**
- Increase `LOG_LEVEL` to `DEBUG`
- Check both main and error logs
- Use grep with appropriate patterns

## Best Practices

1. **Production Systems**
   - Use `INFO` level for general monitoring
   - Monitor `errors_*.log` for failures
   - Set up log rotation and archival
   - Consider centralized logging

2. **Development**
   - Use `DEBUG` for detailed information
   - Review logs after each test run
   - Use logs to understand flow

3. **Debugging Issues**
   - Set `LOG_LEVEL=DEBUG`
   - Reproduce the issue
   - Search logs for error messages
   - Check timestamps to track flow

4. **Performance**
   - Lower log levels = better performance
   - Avoid `DEBUG` in production
   - Monitor log file sizes

## Integration with Monitoring Tools

### Log Aggregation

You can integrate with log aggregation tools:

**Example with Logstash:**
```ruby
input {
  file {
    path => "/path/to/logs/rag_pipeline_*.log"
    type => "rag_pipeline"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} \| %{LOGLEVEL:level} \| %{DATA:module} \| %{GREEDYDATA:message}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
  }
}
```

### Monitoring Scripts

Simple monitoring script:

```python
import os
import time
from pathlib import Path

def monitor_errors(log_dir="logs"):
    error_log = Path(log_dir) / f"errors_{time.strftime('%Y%m%d')}.log"
    
    if error_log.exists():
        with open(error_log) as f:
            errors = f.readlines()
            recent_errors = [e for e in errors if "ERROR" in e]
            
            if len(recent_errors) > 10:
                print(f"⚠️ Warning: {len(recent_errors)} errors detected!")
                for err in recent_errors[-5:]:
                    print(err.strip())
```

## Support

If you encounter issues with logging:

1. Check this documentation
2. Review log configuration in `.env`
3. Verify file permissions
4. Check disk space
5. Review the error log file

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

