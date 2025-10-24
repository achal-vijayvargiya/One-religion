# 🕉️ One Religion - Multi-Religious Text RAG System

A powerful Retrieval-Augmented Generation (RAG) system that allows you to chat with multiple religious texts simultaneously. Compare answers from different religious traditions side-by-side.

## ✨ Features

- **📚 Multi-Book Support**: Chat with Bhagavad Gita, Bible, Quran, and more
- **🔄 Side-by-Side Comparison**: See responses from multiple religious texts simultaneously  
- **💬 Conversation Mode**: Maintain context across multiple questions
- **🎯 Checkbox Selection**: Easy book selection with visual feedback
- **⚡ Pre-processed Vector Stores**: Ready-to-use embeddings included
- **🌐 Streamlit Web Interface**: Beautiful, responsive chat interface
- **🔧 CLI Tools**: Command-line interface for adding new texts

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/achal-vijayvargiya/One-religion.git
cd One-religion
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your OpenRouter API key
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Start Chatting!
- Open `http://localhost:8501`
- Select one or multiple books using checkboxes
- Ask questions and get responses from your selected religious texts

## 📖 Available Religious Texts

| Book | Status | Description |
|------|--------|-------------|
| **Bhagavad Gita** | ✅ Ready | Hindu scripture - conversation between Krishna and Arjuna |
| **Bible** | ✅ Ready | Christian holy book - Old and New Testament |
| **Quran** | 📥 Available | Islamic holy book - revelations to Prophet Muhammad |

## 🎯 How It Works

### Book Selection
- Use checkboxes to select one or multiple religious texts
- Visual indicators show which books are loaded and ready
- At least one book must be selected to start chatting

### Query Processing
- **Single Book**: Standard chat interface with sources
- **Multiple Books**: Side-by-side comparison with book-specific responses
- Each book is queried independently for authentic responses

### Response Display
- **📖 Book Headers**: Clear identification of which text responded
- **💬 Answers**: Direct responses from each religious text
- **📚 Sources**: Page references and relevance scores
- **🔄 Conversation**: Context maintained across multiple questions

## 🔧 Adding New Religious Texts

### Using the Helper Script
```bash
python add_religious_text.py
```

### Manual Method
1. Create directory: `resources/your_religion/`
2. Add PDF file: `resources/your_religion/your_text.pdf`
3. Ingest: `python pipeline.py resources/your_religion/your_text.pdf --book-id your_religion`

## 📁 Project Structure

```
One-religion/
├── app.py                          # 🌐 Streamlit web application
├── pipeline.py                     # 🔧 CLI for PDF ingestion
├── add_religious_text.py          # 📝 Interactive setup script
├── requirements.txt                 # 📦 Python dependencies
├── env.example                     # ⚙️ Environment variables template
├── src/                           # 💻 Source code
│   ├── book_manager.py            # 📚 Multi-book management
│   ├── multi_book_retrieval.py    # 🔍 Multi-book querying
│   ├── vector_store.py            # 🗄️ FAISS vector storage
│   ├── retrieval_engine.py        # 🤖 RAG query engine
│   └── config.py                  # ⚙️ Configuration
├── vector_store/                  # 🗄️ Pre-processed embeddings
│   ├── bhagavad_gita/            # ✅ Bhagavad Gita vectors
│   ├── bible/                    # ✅ Bible vectors
│   └── quran/                    # 📥 Quran vectors (empty)
└── resources/                    # 📄 Original PDFs (excluded from repo)
    ├── bhagavad_gita/            # 📄 Bhagavad Gita PDF
    ├── bible/                    # 📄 Bible PDF
    └── quran/                   # 📄 Quran PDF
```

## 🎨 Interface Features

### Book Selection
- **Checkbox Interface**: Easy multi-selection with visual feedback
- **Status Indicators**: ✅ (loaded) or 📥 (available) for each book
- **Selected Books**: Beautiful gradient badges showing current selection
- **Validation**: Ensures at least one book is selected

### Chat Interface
- **Fixed Input**: Always accessible at the bottom of the screen
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Conversation Mode**: Toggle for context-aware responses
- **Clear Chat**: Reset conversation history

### Side-by-Side Display
- **Multi-Column Layout**: Each book gets its own column
- **Book Headers**: Clear identification of responses
- **Source Information**: Page references and relevance scores
- **Error Handling**: Graceful handling of missing books

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Add your PDF files to the `resources/` directories
3. Set up environment variables in Streamlit Cloud
4. Deploy!

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env

# Run the app
streamlit run app.py
```

## 🔑 Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional
VECTOR_STORE_PATH=vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=openai/gpt-3.5-turbo
```

## 📊 Technical Details

- **Vector Store**: FAISS indices with sentence-transformers embeddings
- **LLM**: OpenRouter API integration (supports multiple providers)
- **Framework**: Streamlit for web interface
- **Processing**: Semantic chunking with agentic grouping
- **Storage**: Book-specific vector stores for independent querying

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your religious text PDFs
4. Test the ingestion and web interface
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Streamlit, FAISS, and OpenRouter API
- Supports multiple religious traditions
- Designed for respectful interfaith dialogue
- Pre-processed vector stores included for immediate use

---

**Ready to explore religious texts? Clone the repo and start chatting!** 🚀