# 🚀 Deployment Guide - Chat with Sacred Texts

## Quick Deploy to Streamlit Cloud (Free)

### 1. Prepare Your Repository

```bash
# Add vector store to Git
git add vector_store/bhagavad_gita/
git add requirements.txt
git commit -m "Add pre-built vector store for deployment"
git push
```

### 2. Create requirements.txt (if not exists)

```txt
streamlit
langchain
pypdf
sentence-transformers
faiss-cpu
openai
python-dotenv
pydantic-settings
```

### 3. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub repository
4. Set main file path: `app.py`
5. Add secrets in the dashboard:
   ```
   OPENROUTER_API_KEY = your_api_key_here
   ```

### 4. Your App is Live! 🎉

Users can immediately:
- ✅ Chat with Bhagavad Gita (pre-loaded)
- ✅ Select multiple books for side-by-side comparison
- ✅ Use conversation mode for follow-up questions

## Adding More Books (CLI Only)

Since the cloud app is read-only, add books locally first:

```bash
# Add Bible
python pipeline.py resources/bible/KJV.pdf --book-id bible

# Add Quran  
python pipeline.py resources/quran/Quran.pdf --book-id quran

# Add custom book
python pipeline.py resources/torah/Torah.pdf --book-id torah
```

Then commit and push:
```bash
git add vector_store/
git commit -m "Add more religious texts"
git push
```

## Features

### ✅ What Works on Cloud
- 💬 Chat interface with all pre-loaded books
- 📚 Multi-book selection and comparison
- 🔄 Side-by-side responses
- 💭 Conversation mode with context
- 🎨 Clean, user-friendly interface

### ❌ What's Disabled on Cloud
- 📄 PDF ingestion (use CLI locally)
- 🔧 Advanced settings (use local app)

## File Structure for Deployment

```
your-repo/
├── app.py                    # Main chat interface
├── requirements.txt          # Dependencies
├── vector_store/            # Pre-built vector stores
│   ├── bhagavad_gita/       # ✅ Included
│   ├── bible/               # Add your own
│   └── quran/               # Add your own
├── src/                     # All source code
└── resources/               # PDF storage (not needed on cloud)
```

## Pro Tips

1. **Test locally first**: `streamlit run app.py`
2. **Check file sizes**: Keep under 100MB total for Git
3. **Use Git LFS** for large files if needed
4. **Monitor usage**: Streamlit Cloud has usage limits on free tier

## Alternative: HuggingFace Spaces

For more storage (50GB free):

1. Go to https://huggingface.co/spaces
2. Create new Space
3. Upload your files
4. Set app file to `app.py`
5. Add secrets in Settings

---

**Your multi-religious chat app is ready to deploy!** 🕉️✝️☪️
