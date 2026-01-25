"""Streamlit UI for X to Instagram Reel Converter."""

import streamlit as st
import requests
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# Page configuration
st.set_page_config(
    page_title="X to Instagram Reel Converter",
    page_icon="📱",
    layout="wide"
)

# API URL
API_URL = config.API_URL

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1DA1F2;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #657786;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📱 X to Instagram Reel Converter</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Transform X/Twitter videos into vertical Instagram Reels with full post context</div>',
    unsafe_allow_html=True
)

# Main container
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # URL input
    st.markdown("### Enter X/Twitter Post URL")
    url_input = st.text_input(
        "URL",
        placeholder="https://x.com/username/status/1234567890",
        label_visibility="collapsed"
    )
    
    # Create button
    create_button = st.button("🎬 Create Reel", type="primary", use_container_width=True)
    
    # Instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. Find an X/Twitter post with a video
        2. Copy the post URL (e.g., `https://x.com/username/status/1234567890`)
        3. Paste it above and click "Create Reel"
        4. Wait 1-3 minutes for processing
        5. Download your vertical MP4 file
        6. Upload to Instagram Reels, TikTok, or YouTube Shorts
        
        **Note:** The video will be formatted as a vertical 1080x1920 MP4 with:
        - Blurred background
        - User avatar and username
        - Post caption
        - Engagement metrics (likes, retweets, comments, views)
        - Original audio preserved
        """)

# Process reel creation
if create_button:
    if not url_input:
        st.error("⚠️ Please enter an X/Twitter URL")
    elif not (url_input.startswith('https://x.com/') or url_input.startswith('https://twitter.com/')):
        st.error("⚠️ Invalid URL format. Please enter a valid X/Twitter post URL")
    else:
        # Show loading spinner
        with st.spinner("🎥 Creating your reel... This may take 1-3 minutes. Please wait..."):
            try:
                # Make API request
                response = requests.post(
                    f"{API_URL}/api/create-reel",
                    json={"url": url_input},
                    timeout=config.MAX_PROCESSING_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    metadata = result.get('metadata', {})
                    filename = result.get('file')
                    
                    # Success message
                    st.success("✅ Reel created successfully!")
                    
                    # Display metrics
                    st.markdown("### 📊 Reel Information")
                    
                    metric_cols = st.columns(4)
                    with metric_cols[0]:
                        st.metric("Username", f"@{metadata.get('username', 'N/A')}")
                    with metric_cols[1]:
                        st.metric("File Size", f"{metadata.get('file_size_mb', 0):.2f} MB")
                    with metric_cols[2]:
                        st.metric("Resolution", "1080×1920")
                    with metric_cols[3]:
                        st.metric("Format", "MP4")
                    
                    # Detailed metadata
                    with st.expander("📝 Post Details"):
                        detail_cols = st.columns(2)
                        with detail_cols[0]:
                            st.markdown(f"**Display Name:** {metadata.get('display_name', 'N/A')}")
                            st.markdown(f"**Likes:** ❤️ {metadata.get('likes', 0):,}")
                            st.markdown(f"**Retweets:** 🔄 {metadata.get('retweets', 0):,}")
                        with detail_cols[1]:
                            st.markdown(f"**Comments:** 💬 {metadata.get('comments', 0):,}")
                            st.markdown(f"**Views:** 👁️ {metadata.get('views', 0):,}")
                            st.markdown(f"**Posted:** {metadata.get('timestamp', 'N/A')}")
                        
                        if metadata.get('caption'):
                            st.markdown(f"**Caption:**")
                            st.text(metadata.get('caption'))
                    
                    # Download button
                    st.markdown("### 📥 Download Your Reel")
                    
                    try:
                        # Fetch the file from API
                        download_response = requests.get(
                            f"{API_URL}/api/download-reel/{filename}",
                            timeout=60
                        )
                        
                        if download_response.status_code == 200:
                            st.download_button(
                                label="⬇️ Download MP4",
                                data=download_response.content,
                                file_name=filename,
                                mime="video/mp4",
                                use_container_width=True
                            )
                            
                            # Upload instructions
                            st.markdown("### 📱 Upload to Social Media")
                            upload_cols = st.columns(3)
                            
                            with upload_cols[0]:
                                st.markdown("""
                                **Instagram Reels:**
                                1. Transfer MP4 to phone
                                2. Open Instagram → Create → Reel
                                3. Select video and share
                                """)
                            
                            with upload_cols[1]:
                                st.markdown("""
                                **TikTok:**
                                1. Transfer MP4 to phone
                                2. Open TikTok → + → Upload
                                3. Select video and post
                                """)
                            
                            with upload_cols[2]:
                                st.markdown("""
                                **YouTube Shorts:**
                                1. Open YouTube app
                                2. → + → Create a Short
                                3. Upload and publish
                                """)
                        else:
                            st.error(f"⚠️ Failed to fetch download file: {download_response.status_code}")
                    
                    except Exception as e:
                        st.error(f"⚠️ Download error: {str(e)}")
                
                else:
                    # Error response
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error occurred')
                    st.error(f"❌ Error: {error_msg}")
                    
                    # Show troubleshooting tips
                    with st.expander("🔧 Troubleshooting"):
                        st.markdown("""
                        **Common issues:**
                        - Make sure the X/Twitter post is public
                        - Verify the post contains a video
                        - Check that the URL is correct
                        - Try updating yt-dlp: `pip install -U yt-dlp`
                        - Ensure FFmpeg is installed on your system
                        
                        **Still having issues?**
                        - Check the backend logs in `logs/app.log`
                        - Verify the Flask API is running
                        - Try a different post URL
                        """)
            
            except requests.Timeout:
                st.error("⏱️ Request timed out. The video might be too long or the server is busy. Please try again.")
            
            except requests.ConnectionError:
                st.error("🔌 Cannot connect to the API. Make sure the Flask backend is running on " + API_URL)
                st.info("Start the backend with: `python app/app_reel.py`")
            
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("Check the logs for more details or try again.")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #657786;">Made with ❤️ for content creators | '
    'Respect copyright and X/Twitter Terms of Service</div>',
    unsafe_allow_html=True
)
