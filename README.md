# X to Instagram Reel Converter

Convert X/Twitter video posts into vertical Instagram Reels with custom overlays.

> **Note:** This branch (`main`) only supports **video tweets**. For image and caption-only tweet support, use the [`image-caption-support`](../../tree/image-caption-support) branch.

## What It Does

- Downloads videos from X/Twitter video posts
- Converts them to vertical 1080x1920 MP4 format
- Adds circular avatar above the video
- Shows username, display name, and caption
- Uses white or black background with the video centered
- Keeps original audio intact
- Provides a simple web interface
- Fast processing with optimized encoding
- **Only works with tweets containing video content**

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
   - Paste an X/Twitter **video post** URL (e.g., `https://x.com/username/status/1234567890`)
   - Select video quality (360p, 480p, 720p, or 1080p)
   - Choose background color (white or black)
   - Click "Create Reel"
   - Wait 1-3 minutes for processing
   - Download your MP4 file

**Important:** Only tweets with video content are supported.

### Option 2: API Only

Start the Flask API:
```bash
python app/app_reel.py
```

Make a POST request:
```bash
curl -X POST http://localhost:5000/api/create-reel \
  -H "Content-Type: application/json" \
  -d '{"url": "https://x.com/username/status/1234567890", "resolution": "720p", "background_color": "white"}'
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
    "https://x.com/username/status/1234567890",
    resolution="720p",
    background_color="white"
)

if output_path:
    print(f"Reel created: {output_path}")
else:
    print(f"Error: {metadata}")
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

## Common Issues

**FFmpeg not found**
Make sure FFmpeg is installed and accessible. Run `ffmpeg -version` to check.

**"Only video tweets are supported" error**
This version only works with tweets containing video content. Text-only or image-only tweets are not supported in the main branch. For image/caption tweet support, switch to the [`image-caption-support`](../../tree/image-caption-support) branch.

**Download fails**
The X/Twitter URL needs to be valid, public, and contain a video. You can try updating yt-dlp with `pip install -U yt-dlp`.

**Slow processing or memory errors**
Change the video preset to "ultrafast" in config.py or select a lower resolution (360p or 480p). Also helps to close other apps and stick to shorter videos.

**API won't connect**
Start the Flask backend before Streamlit. Double-check that the API_URL matches where Flask is actually running.

## Branches

- **`main`** - Video tweets only (current branch)
- **`image-caption-support`** - Supports video tweets, image tweets, and text-only tweets

## License

Educational use only. Please respect X/Twitter's Terms of Service and copyright laws.

## Contributing

Fork it, make it better, send a pull request.
