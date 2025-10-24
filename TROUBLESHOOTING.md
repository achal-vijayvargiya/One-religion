# Troubleshooting Guide

## Context Length Error (Error 400)

### Problem
When processing large documents (like the Bhagavad Gita), you may encounter:
```
Error code: 400 - This endpoint's maximum context length is 131072 tokens. 
However, you requested about 239322 tokens...
```

### Root Cause
The agentic grouper was trying to send information about all chunks simultaneously to the LLM, exceeding the model's context window limit.

### Solution Implemented
The system now uses **batch processing** to handle large documents:

1. **Automatic Batching**: Chunks are processed in configurable batches (default: 50 chunks per batch)
2. **Optimized Prompts**: Reduced token usage by compacting the prompt format
3. **Error Recovery**: Fallback mechanism creates individual groups if a batch fails
4. **Progress Tracking**: Clear console output shows batch processing progress

### Configuration Options

You can customize batch processing by setting environment variables in your `.env` file:

```bash
# Number of chunks to process per batch (default: 50)
GROUPING_BATCH_SIZE=50

# Preview length for each chunk in characters (default: 150)
GROUPING_PREVIEW_LENGTH=150
```

#### Adjusting Batch Size

**If you still get context errors:**
- Reduce `GROUPING_BATCH_SIZE` to 20 or 15
- Reduce `GROUPING_PREVIEW_LENGTH` to 80 or 60

**Current defaults:** `GROUPING_BATCH_SIZE=30`, `GROUPING_PREVIEW_LENGTH=120`

**For persistent issues, try ultra-conservative settings:**
```bash
GROUPING_BATCH_SIZE=15
GROUPING_PREVIEW_LENGTH=80
```

**For smaller models or tighter limits:**
```bash
GROUPING_BATCH_SIZE=25
GROUPING_PREVIEW_LENGTH=100
```

**For larger context models (200K+ tokens):**
```bash
GROUPING_BATCH_SIZE=100
GROUPING_PREVIEW_LENGTH=200
```

### Alternative Solutions

#### Option 1: Disable Agentic Grouping (Fastest)
In the Streamlit UI, uncheck "Enable Agentic Grouping". This will:
- ✅ Process documents faster
- ✅ No API calls for grouping
- ❌ Lose semantic knowledge clustering
- ❌ Less contextual retrieval

#### Option 2: Use a Larger Context Model
Update your `.env` file:
```bash
# Claude 3.5 Sonnet has 200K context
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# GPT-4 Turbo has 128K context
OPENROUTER_MODEL=openai/gpt-4-turbo-preview

# Gemini 1.5 Pro has 1M context (best for large docs)
OPENROUTER_MODEL=google/gemini-pro-1.5
```

#### Option 3: Increase Chunk Size
For fewer chunks overall, increase chunk size in `.env`:
```bash
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```
This creates fewer, larger chunks, reducing total batch count.

### How Batch Processing Works

For a document with 200 chunks (batch size = 50):

```
📦 Processing 200 chunks in batches of 50...
  ⏳ Processing batch 1/4 (chunks 0-49)...
  ✓ Created 8 groups from this batch
  
  ⏳ Processing batch 2/4 (chunks 50-99)...
  ✓ Created 7 groups from this batch
  
  ⏳ Processing batch 3/4 (chunks 100-149)...
  ✓ Created 9 groups from this batch
  
  ⏳ Processing batch 4/4 (chunks 150-199)...
  ✓ Created 6 groups from this batch
  
✅ Total groups created: 30
```

Each batch is processed independently, so:
- ✅ No single request exceeds context limits
- ✅ Failures in one batch don't stop the entire process
- ✅ Progress is visible and trackable
- ⏱️ Processing takes longer (multiple API calls)

### Performance Comparison

| Document Size | Without Batching | With Batching (50) |
|--------------|------------------|-------------------|
| 50 pages | ✅ Works | ✅ Works (1 batch) |
| 200 pages | ❌ Context error | ✅ Works (4-8 batches) |
| 500 pages | ❌ Context error | ✅ Works (10-20 batches) |

### Testing Your Configuration

To test if your settings work:

1. Open the Streamlit app: `streamlit run app.py`
2. Upload your PDF (e.g., Bhagavad-gita-As-It-Is.pdf)
3. Enable "Agentic Grouping"
4. Click "Process PDF"
5. Watch the console for batch processing messages

If you see batch processing messages with no errors, it's working! 🎉

### Additional Tips

1. **Monitor API Usage**: Batch processing makes more API calls, so watch your OpenRouter credits
2. **Processing Time**: Expect 30-60 seconds per batch with most models
3. **Vector Store**: Save the vector store to avoid reprocessing the same document
4. **Error Logs**: Check console output for specific batch failures

### Need More Help?

- Check your OpenRouter API key is valid
- Verify your selected model supports your needs
- Try a smaller test document first
- Consider disabling grouping for very large documents (>1000 pages)

