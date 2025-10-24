# Conversational Mode - Multi-Turn Chat Interface

The RAG system now supports **conversational mode** with full chat history and context-aware responses!

## 🆕 What's New

### Before
- Single questions only
- No memory of previous questions
- Each query was independent

### Now
- 💬 **Full chat interface** - Natural conversation flow
- 🧠 **Memory** - Remembers previous Q&A exchanges
- 🔄 **Context-aware** - Understands follow-up questions
- 🎯 **Query reformulation** - Automatically clarifies vague follow-ups

## ✨ Features

### 1. Chat Interface
Modern chat UI with:
- Message history display
- User/Assistant message bubbles
- Source citations per message
- Smooth scrolling

### 2. Conversation Mode Toggle
- **ON**: Multi-turn conversations with context
- **OFF**: Traditional single-question mode

### 3. Automatic Query Reformulation
Turns vague follow-ups into clear standalone questions:

**Example:**
```
User: What is karma yoga?
AI: Karma yoga is the path of selfless action...

User: How does it differ from bhakti yoga?
(Reformulated internally: "How does karma yoga differ from bhakti yoga in the Bhagavad Gita?")
```

### 4. Conversation History Management
- Stores up to 10 exchanges (configurable)
- Clear chat button
- Persistent within session
- Exportable for analysis

## 🎮 How to Use

### Starting a Conversation

1. **Load/Ingest** your knowledge base
2. Go to **💬 Chat** tab
3. **Enable** "Conversation Mode" (on by default)
4. Start asking questions!

### Example Conversation

```
👤 User: What is the main message of the Bhagavad Gita?

🤖 Assistant: The main message of the Bhagavad Gita is to perform one's duty 
without attachment to results, emphasizing the paths of karma yoga, bhakti yoga, 
and jnana yoga...

👤 User: Tell me more about karma yoga

🤖 Assistant: Karma yoga, as discussed in the Bhagavad Gita, is the path of 
selfless action...

👤 User: What chapter discusses this?

🤖 Assistant: Karma yoga is primarily discussed in Chapter 3 (Karma Yoga) and 
Chapter 5 (Karma Sannyasa Yoga)...
```

### Advanced Options

**Number of sources**: Control how many documents to retrieve (1-10)

**Conversation Mode**: Toggle on/off anytime

**Clear Chat**: Reset conversation history

## 🔧 Technical Details

### Architecture

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Conversation Manager    │ ← Stores history
│ - Last 10 exchanges     │
│ - User questions        │
│ - AI responses          │
│ - Source citations      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Query Reformulation     │ ← Makes followups clear
│ (if conversation mode)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Vector Search           │ ← Find relevant docs
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Answer Generation       │ ← Generate response
│ (with conversation ctx) │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Store in History        │ ← Save for next turn
└─────────────────────────┘
```

### Query Reformulation

When you ask a follow-up question like "What about that?", the system:

1. **Retrieves** last 3 conversation exchanges
2. **Sends** to LLM with reformulation prompt
3. **Gets** standalone question
4. **Uses** reformulated query for vector search

**Example reformulations:**
- "What about Krishna?" → "What role does Krishna play in the Bhagavad Gita?"
- "And Arjuna?" → "What is Arjuna's role in the Bhagavad Gita?"
- "Tell me more" → "Can you provide more details about karma yoga in the Bhagavad Gita?"

### Conversation Context in Prompts

The system includes conversation history in the LLM prompt:

```
System: You are a knowledgeable assistant...

Conversation History (for context only):
Q: What is karma yoga?
A: Karma yoga is...
Q: How does it differ from bhakti yoga?
A: The main differences are...

[Current question and context documents...]
```

This helps the AI:
- ✅ Maintain coherent conversation
- ✅ Avoid repeating information
- ✅ Reference previous answers
- ✅ Understand pronouns and references

## ⚙️ Configuration

### In Code

```python
from src.retrieval_engine import RetrievalEngine
from src.conversation_manager import ConversationManager

# Enable conversation (default)
engine = RetrievalEngine(enable_conversation=True)

# Disable conversation (single-question mode)
engine = RetrievalEngine(enable_conversation=False)

# Custom conversation settings
conversation = ConversationManager(max_history=20)  # Store 20 exchanges
```

### Conversation Manager Settings

**Max History**: Default 10 exchanges
- Change in `src/conversation_manager.py`
- Or pass to `ConversationManager(max_history=N)`

**Context Window**: Default 3 exchanges
- Used for query reformulation
- Adjustable in `retrieval_engine.py`

## 📊 API Reference

### ConversationManager

```python
from src.conversation_manager import ConversationManager

conv = ConversationManager(max_history=10)

# Add exchange
conv.add_exchange(
    user_query="What is karma?",
    assistant_response="Karma is...",
    sources=[...],
    metadata={...}
)

# Get history
history = conv.get_history(last_n=5)

# Get conversation context for reformulation
context = conv.get_conversation_context(last_n=3)

# Clear history
conv.clear()

# Export for saving
data = conv.export_history()

# Check length
num_exchanges = len(conv)
```

### RetrievalEngine

```python
from src.retrieval_engine import RetrievalEngine

engine = RetrievalEngine(enable_conversation=True)

# Query with conversation context
result = engine.query(
    question="What about Krishna?",
    k=5,
    use_conversation_context=True  # Default
)

# Clear conversation
engine.clear_conversation()

# Get conversation history
history = engine.get_conversation_history(last_n=5)

# Export conversation
data = engine.export_conversation()
```

## 💡 Best Practices

### For Users

1. **Start broad, then narrow**
   - "What is the Bhagavad Gita about?"
   - "Tell me about karma yoga"
   - "Which chapter discusses this?"

2. **Use natural language**
   - "What does Krishna say about this?"
   - "Can you explain that concept?"
   - "What's the difference?"

3. **Clear chat when changing topics**
   - Prevents confusion from unrelated context

### For Developers

1. **Monitor conversation length**
   - Longer histories = more tokens
   - Balance between context and cost

2. **Test reformulation**
   - Check logs to see reformulated queries
   - Adjust prompts if needed

3. **Handle errors gracefully**
   - Reformulation failures fall back to original query
   - Conversation continues even with errors

## 🐛 Troubleshooting

### Conversation Not Working

**Check:**
1. Conversation mode is enabled (toggle in UI)
2. Knowledge base is loaded
3. Check logs: `logs/rag_pipeline_*.log`

### Follow-up Questions Don't Work Well

**Try:**
1. Be more specific in follow-ups
2. Check if query reformulation is working (check logs)
3. Reduce conversation history length
4. Switch to better model (Claude/GPT-4)

### Chat History Gets Confused

**Solution:**
1. Click "Clear Chat" button
2. Start new conversation
3. Reduce `max_history` if needed

## 📝 Logging

Conversation features are fully logged:

```bash
# View conversation operations
grep "conversation" logs/rag_pipeline_*.log

# View query reformulations
grep "reformulated" logs/rag_pipeline_*.log

# View conversation additions
grep "Exchange added" logs/rag_pipeline_*.log
```

## 🚀 Future Enhancements

Potential improvements:
- [ ] Conversation persistence (save/load between sessions)
- [ ] Conversation export to JSON/CSV
- [ ] Conversation analytics dashboard
- [ ] Multi-user conversations
- [ ] Conversation branching
- [ ] Conversation summarization

## 🎓 Example Use Cases

### 1. Learning about a Topic
```
"What is dharma?" → "How does it relate to karma?" → "Give me an example"
```

### 2. Comparative Analysis
```
"What is karma yoga?" → "What is bhakti yoga?" → "Compare them"
```

### 3. Deep Dive
```
"Who is Arjuna?" → "What is his dilemma?" → "How does Krishna help?"
```

### 4. Finding Specific Information
```
"What chapters discuss yoga?" → "Tell me about chapter 6" → "What are the key verses?"
```

## 📚 References

- `src/conversation_manager.py` - Conversation history management
- `src/retrieval_engine.py` - Query reformulation and context handling
- `app.py` - Chat interface implementation

---

**Enjoy conversing with your documents!** 💬✨

