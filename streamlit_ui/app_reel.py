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
st.markdown('<div class="main-header">X to Instagram Reel Converter</div>', unsafe_allow_html=True)
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
    
    # Resolution selector
    st.markdown("### Video Quality")
    resolution = st.select_slider(
        "Select resolution (lower = faster processing)",
        options=["360p", "480p", "720p", "1080p"],
        value="720p",
        label_visibility="collapsed"
    )
    st.caption(f"Selected: **{resolution}** {'Fast' if resolution in ['360p', '480p'] else 'HD' if resolution == '720p' else 'Full HD'}")
    
    # Background color selector
    st.markdown("### Background Color")
    background_color = st.selectbox(
        "Choose background color",
        options=["White", "Black"],
        index=0,
        label_visibility="collapsed"
    )
    st.caption(f"Background: **{background_color}**")
    
    # Create button
    create_button = st.button("Create Reel", type="primary", use_container_width=True)
    
    # Instructions
    with st.expander("How to use"):
        st.markdown("""
        1. Find an X/Twitter post with a video
        2. Copy the post URL (e.g., `https://x.com/username/status/1234567890`)
        3. Select video quality (360p-1080p)
        4. Click "Create Reel"
        5. Preview and download your video
        
        **Resolution Guide:**
        - **360p**: Fastest (15-30 seconds) - Good for quick sharing
        - **480p**: Fast (30-60 seconds) - Balanced quality/speed
        - **720p**: Recommended (60-90 seconds) - Great quality
        - **1080p**: Best Quality (2-3 minutes) - Instagram Reels HD
        """)

# Initialize session state for persistence
if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

# Process reel creation
if create_button:
    if not url_input:
        st.error("Please enter an X/Twitter URL")
    elif not (url_input.startswith('https://x.com/') or url_input.startswith('https://twitter.com/')):
        st.error("Invalid URL format. Please enter a valid X/Twitter post URL")
    else:
        # Show loading spinner
        estimated_time = "15-30 seconds" if resolution == "360p" else "30-60 seconds" if resolution == "480p" else "60-90 seconds" if resolution == "720p" else "2-3 minutes"
        with st.spinner(f"Creating your reel in {resolution}... This may take {estimated_time}. Please wait..."):
            try:
                # Make API request with resolution and background color
                response = requests.post(
                    f"{API_URL}/api/create-reel",
                    json={"url": url_input, "resolution": resolution, "background_color": background_color.lower()},
                    timeout=config.MAX_PROCESSING_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    metadata = result.get('metadata', {})
                    filename = result.get('file')
                    
                    # Fetch the video file
                    download_response = requests.get(
                        f"{API_URL}/api/download-reel/{filename}",
                        timeout=120
                    )
                    
                    if download_response.status_code == 200:
                        # Store in session state for persistence
                        st.session_state.video_data = download_response.content
                        st.session_state.metadata = metadata
                        st.session_state.filename = filename
                        
                        st.success("Reel created successfully!")
                    else:
                        st.error(f"Failed to fetch video: {download_response.status_code}")
                
                else:
                    # Error response
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error occurred')
                    st.error(f"Error: {error_msg}")
                    
                    # Show troubleshooting tips
                    with st.expander("Troubleshooting"):
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
                st.error("Request timed out. The video might be too long or the server is busy. Please try again.")
            
            except requests.ConnectionError:
                st.error("Cannot connect to the API. Make sure the Flask backend is running on " + API_URL)
                st.info("Start the backend with: `python app/app_reel.py`")
            
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.info("Check the logs for more details or try again.")

# Display video preview and download if available in session state
if st.session_state.video_data:
    st.markdown("---")
    
    with col2:
        # Video preview
        st.markdown("### Video Preview")
        st.video(st.session_state.video_data)
        
        # Metadata display
        metadata = st.session_state.metadata
        st.markdown("### Reel Information")
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("Username", f"@{metadata.get('username', 'N/A')}")
        with metric_cols[1]:
            file_size = len(st.session_state.video_data) / (1024 * 1024)
            st.metric("File Size", f"{file_size:.2f} MB")
        with metric_cols[2]:
            st.metric("Resolution", "1080×1920")
        with metric_cols[3]:
            st.metric("Format", "MP4")
        
        # Detailed metadata
        with st.expander("Post Details"):
            if metadata.get('display_name'):
                st.markdown(f"**Display Name:** {metadata.get('display_name', 'N/A')}")
            if metadata.get('caption'):
                st.markdown(f"**Caption:**")
                st.text(metadata.get('caption'))
            if metadata.get('timestamp'):
                st.markdown(f"**Posted:** {metadata.get('timestamp', 'N/A')}")
        
        # Persistent download button
        st.markdown("### Download Your Reel")
        st.download_button(
            label="Download MP4",
            data=st.session_state.video_data,
            file_name=st.session_state.filename,
            mime="video/mp4",
            use_container_width=True,
            key="download_btn"
        )
        
        # Clear button
        if st.button("Create New Reel", use_container_width=True):
            st.session_state.video_data = None
            st.session_state.metadata = None
            st.session_state.filename = None
            st.rerun()
        
        # Upload instructions
        st.markdown("### Upload to Social Media")
        upload_cols = st.columns(3)
        
        with upload_cols[0]:
            st.markdown("""
            **Instagram Reels:**
            1. Download MP4
            2. Transfer to phone
            3. Instagram → Reel → Upload
            """)
        
        with upload_cols[1]:
            st.markdown("""
            **TikTok:**
            1. Download MP4
            2. TikTok → + → Upload
            3. Post video
            """)
        
        with upload_cols[2]:
            st.markdown("""
            **YouTube Shorts:**
            1. Download MP4
            2. YouTube → Create Short
            3. Upload & publish
            """)


# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #657786;">Made for content creators | '
    'Respect copyright and X/Twitter Terms of Service</div>',
    unsafe_allow_html=True
)
