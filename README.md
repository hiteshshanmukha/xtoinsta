# 📱 X to Instagram Reel Converter

Convert X/Twitter videos to Instagram Reels with beautiful overlays including avatar, username, caption, and timestamp.

## 🚀 Deploy to Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Quick Deploy Steps:

1. **Push to GitHub:**
   ```bash
   cd F:\xtoinsta
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `xtoinsta` repository
   - Railway auto-detects Python and deploys!
   - FFmpeg is automatically included ✅

3. **Access Your App:**
   - Railway generates a public URL (e.g., `https://xtoinsta-production.up.railway.app`)
   - Click the URL to open your app
   - Access from ANY device - mobile, tablet, desktop!

## Features

- 🎥 Downloads video from X/Twitter posts
- 🖼️ Creates vertical 1080x1920 MP4 optimized for Instagram Reels
- 👤 Includes circular avatar
- 📝 Displays username, display name, and caption above video
- ⏰ Shows timestamp
- 🎨 White background with centered video
- 🔊 Preserves original audio
- 🌐 Web UI with Streamlit
- ⚡ Ultra-fast processing (optimized encoding)

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ ReelGenerator   │─────▶│   yt-dlp     │
│                 │      └──────────────┘
│   - Metadata    │
│   - Avatar      │      ┌──────────────┐
│   - Video       │─────▶│   moviepy    │
│   - Overlay     │      └──────────────┘
└─────────────────┘
```

## Requirements

### System Requirements

- **Python 3.8+**
- **FFmpeg** (required for video processing)

#### Installing FFmpeg

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

1. **Clone or download this project**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify FFmpeg installation:**
   ```bash
   ffmpeg -version
   ```

## Usage

### Option 1: Web UI (Recommended)

1. **Start the Flask API backend:**
   ```bash
   python app/app_reel.py
   ```
   The API will run on `http://localhost:5000`

2. **In a new terminal, start the Streamlit UI:**
   ```bash
   streamlit run streamlit_ui/app_reel.py
   ```
   The UI will open in your browser at `http://localhost:8501`

3. **Create a reel:**
   - Paste an X/Twitter post URL (e.g., `https://x.com/username/status/1234567890`)
   - Click "🎬 Create Reel"
   - Wait 1-3 minutes for processing
   - Download your MP4 file

### Option 2: API Only

Start the Flask API:
```bash
python app/app_reel.py
```

Make a POST request:
```bash
curl -X POST http://localhost:5000/api/create-reel \
  -H "Content-Type: application/json" \
  -d '{"url": "https://x.com/username/status/1234567890"}'
```

Download the reel:
```bash
curl -O http://localhost:5000/api/download-reel/reel_1234567890.mp4
```

### Option 3: Python Script

```python
from app.reel_generator import ReelGenerator

generator = ReelGenerator()
output_path, metadata = generator.create_reel_from_url(
    "https://x.com/username/status/1234567890"
)

if output_path:
    print(f"✅ Reel created: {output_path}")
else:
    print(f"❌ Error: {metadata}")
```

## Project Structure

```
xtoinsta/
├── app/
│   ├── __init__.py
│   ├── reel_generator.py    # Core video processing logic
│   └── app_reel.py          # Flask API
├── streamlit_ui/
│   ├── __init__.py
│   └── app_reel.py          # Streamlit web interface
├── downloads/               # Output reels (auto-created)
├── logs/                    # Application logs (auto-created)
├── tests/
│   └── test_reel_generator.py
├── config.py               # Configuration settings
├── logging_config.py       # Logging setup
├── requirements.txt        # Python dependencies
├── quickstart.py          # Quick test script
└── README.md
```

## Uploading to Social Media

### Instagram Reels
1. Transfer the MP4 to your phone
2. Open Instagram → Create → Reel
3. Select your video
4. Add music, effects, or text if desired
5. Share

### TikTok
1. Transfer the MP4 to your phone
2. Open TikTok → + → Upload
3. Select your video
4. Add effects and post

### YouTube Shorts
1. Open YouTube app → + → Create a Short
2. Upload your video
3. Add title and publish

## Configuration

Edit [config.py](config.py) to customize:

- **Video resolution:** `REEL_WIDTH`, `REEL_HEIGHT`
- **Video codec:** `VIDEO_CODEC`, `VIDEO_PRESET`
- **Text sizes:** `USERNAME_FONT_SIZE`, `CAPTION_FONT_SIZE`, etc.
- **Processing timeout:** `MAX_PROCESSING_TIMEOUT`

Environment variables:
```bash
export VIDEO_PRESET=fast          # Encoding speed (ultrafast, fast, medium, slow)
export MAX_PROCESSING_TIMEOUT=600 # Max seconds for processing
export FLASK_PORT=5000            # API port
export API_URL=http://localhost:5000  # API base URL
```

## Testing

Run tests:
```bash
pytest tests/ -v
```

## Troubleshooting

### "FFmpeg not found"
- Ensure FFmpeg is installed and in your PATH
- Test: `ffmpeg -version`

### "Failed to download video"
- Check if the X/Twitter URL is valid and public
- Ensure the post contains a video
- Try updating yt-dlp: `pip install -U yt-dlp`

### "Memory error" or slow processing
- Lower the video preset in config.py (use "ultrafast")
- Close other applications
- Process shorter videos

### API connection errors
- Ensure Flask backend is running before starting Streamlit
- Check the API_URL in Streamlit matches Flask host/port

## License

This project is for educational purposes. Respect X/Twitter's Terms of Service and copyright when downloading content.

## Contributing

Feel free to fork, improve, and submit pull requests!

---

**Made with ❤️ for content creators**
