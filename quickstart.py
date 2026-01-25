"""Quickstart script to test the X to Instagram Reel Converter."""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from app.reel_generator import ReelGenerator
from logging_config import get_logger

logger = get_logger(__name__)


def main():
    """Run a quick test of the reel generator."""
    print("=" * 70)
    print("X to Instagram Reel Converter - Quickstart Test")
    print("=" * 70)
    print()
    
    # Check if URL provided as argument
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        # Prompt for URL
        print("Please enter an X/Twitter post URL with a video:")
        print("Example: https://x.com/username/status/1234567890")
        print()
        test_url = input("URL: ").strip()
    
    if not test_url:
        print("❌ No URL provided. Exiting.")
        return
    
    # Validate URL format
    if not (test_url.startswith('https://x.com/') or test_url.startswith('https://twitter.com/')):
        print("❌ Invalid URL format. Please use a valid X/Twitter post URL.")
        return
    
    print()
    print(f"🎬 Creating reel for: {test_url}")
    print("⏳ This may take 1-3 minutes depending on video length...")
    print()
    
    try:
        # Initialize generator
        generator = ReelGenerator()
        
        # Create reel
        output_path, metadata = generator.create_reel_from_url(test_url)
        
        if output_path:
            # Success!
            print("=" * 70)
            print("✅ SUCCESS! Reel created successfully!")
            print("=" * 70)
            print()
            print(f"📁 Output file: {output_path}")
            print(f"📊 File size: {output_path.stat().st_size / (1024 * 1024):.2f} MB")
            print()
            print("📝 Post Details:")
            print(f"   Username: @{metadata.get('username', 'N/A')}")
            print(f"   Display Name: {metadata.get('display_name', 'N/A')}")
            print(f"   Likes: ❤️  {metadata.get('likes', 0):,}")
            print(f"   Retweets: 🔄 {metadata.get('retweets', 0):,}")
            print(f"   Comments: 💬 {metadata.get('comments', 0):,}")
            print(f"   Views: 👁️  {metadata.get('views', 0):,}")
            print(f"   Posted: {metadata.get('timestamp', 'N/A')}")
            print()
            if metadata.get('caption'):
                print(f"   Caption: {metadata.get('caption')[:100]}...")
            print()
            print("=" * 70)
            print("🎉 You can now upload this to Instagram Reels, TikTok, or YouTube Shorts!")
            print("=" * 70)
        else:
            # Failed
            error_msg = metadata.get('error', 'Unknown error')
            print()
            print("=" * 70)
            print("❌ FAILED to create reel")
            print("=" * 70)
            print()
            print(f"Error: {error_msg}")
            print()
            print("💡 Troubleshooting tips:")
            print("   - Make sure the X/Twitter post is public")
            print("   - Verify the post contains a video")
            print("   - Check that FFmpeg is installed")
            print("   - Try updating yt-dlp: pip install -U yt-dlp")
            print("   - Check logs in logs/app.log for more details")
            print()
    
    except KeyboardInterrupt:
        print()
        print("⚠️  Process interrupted by user")
    
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ UNEXPECTED ERROR")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Please check logs/app.log for more details")
        print()


if __name__ == "__main__":
    main()
