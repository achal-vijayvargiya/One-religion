# One Religion - Multi-Religious Text RAG System

## 🚀 Quick Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/achal-vijayvargiya/One-religion.git
cd One-religion
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
cp env.example .env
# Edit .env with your API keys
```

### 4. Add Religious Text PDFs
Since large PDF files are excluded from the repository, you need to add them manually:

#### For Bhagavad Gita:
```bash
# Download and place Bhagavad Gita PDF in:
resources/bhagavad_gita/Bhagavad-gita-As-It-Is.pdf
```

#### For Bible:
```bash
# Download and place Bible PDF in:
resources/bible/bible.pdf
```

#### For Quran:
```bash
# Download and place Quran PDF in:
resources/quran/quran.pdf
```

### 5. Ingest PDFs into Vector Stores
```bash
# Bhagavad Gita
python pipeline.py resources/bhagavad_gita/Bhagavad-gita-As-It-Is.pdf --book-id bhagavad_gita

# Bible
python pipeline.py resources/bible/bible.pdf --book-id bible

# Quran
python pipeline.py resources/quran/quran.pdf --book-id quran
```

### 6. Run the Web Application
```bash
streamlit run app.py
```

## 📚 Supported Religious Texts

- **Bhagavad Gita** (Hindu Scripture)
- **Bible** (Christian Scripture) 
- **Quran** (Islamic Scripture)
- **Extensible** for more religious texts

## 🎯 Features

- ✅ **Multi-book selection** with checkboxes
- ✅ **Side-by-side comparison** of responses
- ✅ **Conversation mode** with context
- ✅ **CLI-based PDF ingestion**
- ✅ **Responsive web interface**
- ✅ **Fixed sidebar** with book status
- ✅ **Real-time chat** with religious texts

## 🔧 Adding New Religious Texts

1. Create a new directory in `resources/`:
   ```bash
   mkdir resources/new_religion
   ```

2. Add your PDF file:
   ```bash
   cp your_religious_text.pdf resources/new_religion/
   ```

3. Ingest the PDF:
   ```bash
   python pipeline.py resources/new_religion/your_religious_text.pdf --book-id new_religion
   ```

4. The new book will automatically appear in the web interface!

## 📖 Usage Examples

### Web Interface
1. Open `http://localhost:8501`
2. Select one or multiple books using checkboxes
3. Ask questions and get responses
4. Compare answers from different religious texts

### CLI Usage
```bash
# Query a single book
python -c "
from src.multi_book_retrieval import MultiBookRetrieval
from src.book_manager import BookManager

bm = BookManager()
bm.load_book('bhagavad_gita')
mbr = MultiBookRetrieval(bm)
result = mbr.query_multiple_books('What is the meaning of life?', ['bhagavad_gita'])
print(result)
"
```

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

## 📁 Project Structure

```
One-religion/
├── app.py                          # Streamlit web application
├── pipeline.py                     # CLI for PDF ingestion
├── requirements.txt                 # Python dependencies
├── env.example                     # Environment variables template
├── src/                           # Source code
│   ├── book_manager.py            # Multi-book management
│   ├── multi_book_retrieval.py    # Multi-book querying
│   ├── vector_store.py            # FAISS vector storage
│   ├── retrieval_engine.py        # RAG query engine
│   └── config.py                  # Configuration
├── resources/                     # Religious text PDFs
│   ├── bhagavad_gita/            # Bhagavad Gita PDFs
│   ├── bible/                     # Bible PDFs
│   └── quran/                    # Quran PDFs
└── vector_store/                 # Generated vector stores
    ├── bhagavad_gita/            # Bhagavad Gita vectors
    ├── bible/                    # Bible vectors
    └── quran/                    # Quran vectors
```

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
