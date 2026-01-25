# Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select this repo
4. Railway will auto-detect and deploy
5. Access via the generated URL (works on mobile!)

**Deploy Button:**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Option 2: Render (Free Tier Available)
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Render will use `render.yaml` automatically
5. Click "Create Web Service"
6. Access via `https://your-app.onrender.com`

### Option 3: Streamlit Cloud (Streamlit Only)
1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect GitHub repo
4. Set:
   - Main file: `streamlit_ui/app_reel.py`
   - Python version: 3.12
5. Deploy - gets a URL like `https://yourapp.streamlit.app`

### Option 4: Ngrok (Quick Local Access from Mobile)
```bash
# Install ngrok
choco install ngrok

# Run Streamlit
streamlit run streamlit_ui/app_reel.py

# In another terminal, expose port 8501
ngrok http 8501
```
Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and access from mobile!

### Option 5: Vercel (Serverless)
```bash
npm i -g vercel
vercel --prod
```

## Performance Optimizations (Already Applied)
- ✅ Video preset: `ultrafast` (6x faster encoding)
- ✅ FPS: Reduced to 24 (20% faster)
- ✅ Efficient avatar caching

## Post-Deployment
- Access the Streamlit UI URL from any device
- Paste X/Twitter video URL
- Download the converted reel
- Share directly to Instagram!

## Troubleshooting
- **FFmpeg errors**: Railway/Render include FFmpeg by default
- **Memory issues**: Upgrade to paid tier for longer videos
- **Slow processing**: Already optimized with `ultrafast` preset
