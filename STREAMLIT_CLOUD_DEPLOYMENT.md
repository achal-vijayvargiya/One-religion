# 🚀 Streamlit Cloud Deployment Guide

## Step-by-Step Deployment Instructions

### 1. Fork the Repository
1. Go to https://github.com/achal-vijayvargiya/One-religion
2. Click "Fork" to create your own copy
3. Clone your fork locally (optional for development)

### 2. Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub account
4. Select your forked repository: `your-username/One-religion`
5. Set the main file path: `app.py`
6. Click "Deploy!"

### 3. Configure Secrets (API Keys)
1. In your Streamlit Cloud dashboard, go to your app
2. Click the "Settings" gear icon
3. Go to the "Secrets" tab
4. Add the following secrets:

```toml
[secrets]
OPENROUTER_API_KEY = "your_actual_openrouter_api_key"
```

### 4. Get Your OpenRouter API Key
1. Go to https://openrouter.ai/
2. Sign up for an account
3. Go to https://openrouter.ai/keys
4. Create a new API key
5. Copy the key and paste it in Streamlit secrets

### 5. Restart Your App
1. In Streamlit Cloud, click "Restart app"
2. Wait for the app to restart
3. Your app should now work without the API key error!

## 🔧 Troubleshooting

### Error: "OPENROUTER_API_KEY not found"
- **Solution**: Make sure you've added the secret in Streamlit Cloud settings
- **Check**: Go to Settings → Secrets and verify the key is there
- **Format**: Use the exact format shown above (no quotes around the key name)

### Error: "Vector store not found"
- **Solution**: The app includes pre-processed vector stores for Bhagavad Gita and Bible
- **Note**: Quran vector store is empty - you can add it later via CLI

### App Loading Slowly
- **Normal**: First load takes time to download dependencies
- **Wait**: Give it 2-3 minutes for initial setup
- **Subsequent loads**: Much faster after first deployment

## 📚 What's Included

### ✅ Pre-processed Vector Stores
- **Bhagavad Gita**: Ready to chat immediately
- **Bible**: Ready to chat immediately  
- **Quran**: Directory structure ready (needs PDF)

### ✅ Features Available
- Multi-book selection with checkboxes
- Side-by-side response comparison
- Conversation mode with context
- Responsive web interface
- Fixed sidebar with book status

## 🎯 Usage After Deployment

1. **Select Books**: Use checkboxes to choose religious texts
2. **Ask Questions**: Type questions in the chat input
3. **Compare Responses**: See answers from multiple books side-by-side
4. **View Sources**: Click expanders to see source pages and relevance

## 🔄 Adding More Books

### Via CLI (Local Development)
```bash
# Add a new religious text
python add_religious_text.py

# Or manually
python pipeline.py path/to/your.pdf --book-id your_religion
```

### Via Streamlit Cloud
- Currently not supported (CLI-only)
- Books must be added locally and pushed to repository
- Vector stores are included in the repository

## 📊 App Structure

```
Your Streamlit Cloud App:
├── app.py                    # Main Streamlit application
├── src/                      # Source code
├── vector_store/            # Pre-processed embeddings
│   ├── bhagavad_gita/       # ✅ Ready
│   ├── bible/              # ✅ Ready
│   └── quran/              # 📥 Empty
└── requirements.txt         # Dependencies
```

## 🎉 Success!

Once deployed, your app will be available at:
`https://your-app-name.streamlit.app`

**Features ready to use:**
- ✅ Chat with Bhagavad Gita
- ✅ Chat with Bible  
- ✅ Compare both books side-by-side
- ✅ Conversation mode with context
- ✅ Responsive design for all devices

## 🆘 Need Help?

1. **Check Streamlit Cloud logs** for error messages
2. **Verify secrets** are correctly set
3. **Restart the app** if changes don't take effect
4. **Check GitHub repository** for latest updates

---

**Your multi-religious RAG system is now live on Streamlit Cloud!** 🕉️✝️☪️
