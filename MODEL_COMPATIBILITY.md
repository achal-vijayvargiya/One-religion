# Model Compatibility Guide

This guide helps you choose the right LLM model for the RAG pipeline via OpenRouter.

## ✅ Fully Supported Models

These models support all features including system messages:

### Anthropic (Claude) - **RECOMMENDED**
- ✅ `anthropic/claude-3-opus` - Most capable, 200K context
- ✅ `anthropic/claude-3.5-sonnet` - Best balance, 200K context
- ✅ `anthropic/claude-3-sonnet` - Good performance, 200K context
- ✅ `anthropic/claude-3-haiku` - Fast and cheap, 200K context

**Best for:** Large documents, complex reasoning, JSON output

### OpenAI (GPT)
- ✅ `openai/gpt-4-turbo-preview` - Very capable, 128K context
- ✅ `openai/gpt-4` - Reliable, 8K context
- ✅ `openai/gpt-3.5-turbo` - Fast and cheap, 16K context

**Best for:** General use, good JSON output

### Meta (Llama)
- ✅ `meta-llama/llama-3-70b-instruct` - Strong performance
- ✅ `meta-llama/llama-3-8b-instruct` - Fast, lower cost

**Best for:** Cost-effective option with good quality

### Mistral AI
- ✅ `mistralai/mistral-large` - Strong performance
- ✅ `mistralai/mistral-medium` - Good balance
- ✅ `mistralai/mixtral-8x7b-instruct` - Cost-effective

**Best for:** European data residency, good performance

### Cohere
- ✅ `cohere/command-r-plus` - Strong for RAG
- ✅ `cohere/command-r` - Good performance

**Best for:** Search and retrieval tasks

## ⚠️ Models with Limitations

These models work but have some limitations:

### Google (Gemini)
- ⚠️ `google/gemini-pro-1.5` - Works (1M context!) but may have quirks
- ⚠️ `google/gemini-pro` - Works with merged prompts
- ❌ `google/gemma-2-27b-it` - **NO SYSTEM MESSAGE SUPPORT**
- ❌ `google/gemma-2-9b-it` - **NO SYSTEM MESSAGE SUPPORT**

**Note:** Gemma models do NOT support system messages. While the code now handles this automatically by merging system instructions into the user prompt, we recommend using Claude or GPT for best results.

**Best for:** Very long documents (Gemini Pro 1.5 only)

## 🚫 Not Recommended

- ❌ **Gemma models** - Limited instruction following, no system messages
- ❌ **Very small models (<7B params)** - May struggle with JSON output
- ❌ **Models with <8K context** - May fail on larger batches

## 📊 Performance Comparison

| Model | Speed | Cost | Quality | Context | JSON Output |
|-------|-------|------|---------|---------|-------------|
| Claude 3.5 Sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 200K | Excellent |
| GPT-4 Turbo | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 128K | Excellent |
| GPT-3.5 Turbo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 16K | Good |
| Llama 3 70B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8K | Good |
| Gemini Pro 1.5 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 1M | Fair |
| Gemma 27B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 8K | Poor |

## 🔧 Configuration

Set your model in `.env`:

```bash
# Recommended: Claude 3.5 Sonnet (best balance)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Alternative: GPT-4 Turbo
OPENROUTER_MODEL=openai/gpt-4-turbo-preview

# Budget option: GPT-3.5 Turbo
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# For very large documents: Gemini Pro 1.5
OPENROUTER_MODEL=google/gemini-pro-1.5
```

## 🐛 Error Messages and Solutions

### "Developer instruction is not enabled"
**Error:** Models like Gemma don't support system messages.

**Solution:** The code now handles this automatically! But for best results, use Claude or GPT models.

**If it still fails:**
```bash
# Switch to a compatible model in .env
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

### "Context length exceeded"
**Error:** Model's context window is too small.

**Solution:**
1. Reduce batch size in `.env`:
   ```bash
   GROUPING_BATCH_SIZE=20
   GROUPING_PREVIEW_LENGTH=100
   ```

2. Or use a model with larger context:
   ```bash
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # 200K context
   ```

### Poor JSON Output
**Error:** Model returns invalid JSON or doesn't follow instructions.

**Solution:** Use Claude or GPT models, which are better at structured output:
```bash
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

## 💡 Recommendations by Use Case

### For Production
**Best:** `anthropic/claude-3.5-sonnet`
- Excellent quality
- 200K context (handles large documents)
- Reliable JSON output
- Good speed

### For Development/Testing
**Best:** `openai/gpt-3.5-turbo`
- Fast responses
- Very cheap
- Good enough for testing
- Reliable

### For Very Large Documents
**Best:** `google/gemini-pro-1.5`
- 1M context window
- Can handle entire books
- Note: May need prompt adjustments

### For Cost Optimization
**Best:** `meta-llama/llama-3-8b-instruct`
- Very cheap
- Decent quality
- Fast
- Good for high-volume use

## 🔄 System Message Compatibility

The code automatically handles models that don't support system messages by merging the system instruction into the user prompt. However, results may vary:

**Models with native system message support (best):**
- ✅ All Anthropic Claude models
- ✅ All OpenAI GPT models
- ✅ Meta Llama 3 models
- ✅ Mistral models

**Models without system message support (automatically handled):**
- ⚠️ Google Gemma models
- ⚠️ Some Google Gemini models

## 📝 Testing a New Model

To test if a model works well:

1. Set it in `.env`:
   ```bash
   OPENROUTER_MODEL=your/model-name
   ```

2. Enable debug logging:
   ```bash
   LOG_LEVEL=DEBUG
   ```

3. Run a small test:
   ```bash
   python pipeline.py resources/test.pdf --no-save
   ```

4. Check logs:
   ```bash
   tail -f logs/rag_pipeline_*.log
   ```

5. Look for:
   - ✅ Successful JSON parsing
   - ✅ Reasonable groupings
   - ✅ No repeated errors

## 🆘 Support

If you encounter issues with a specific model:

1. Check [OpenRouter model documentation](https://openrouter.ai/models)
2. Review logs in `logs/rag_pipeline_*.log`
3. Try a recommended model from this guide
4. Enable DEBUG logging to see detailed information

## 📚 References

- [OpenRouter Models](https://openrouter.ai/models)
- [Anthropic Claude](https://www.anthropic.com/claude)
- [OpenAI GPT](https://platform.openai.com/docs/models)
- [Google AI Studio](https://ai.google.dev/)
- [Meta Llama](https://ai.meta.com/llama/)

