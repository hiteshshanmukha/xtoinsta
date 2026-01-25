"""Core ReelGenerator class for creating Instagram Reels from X/Twitter posts."""

import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# MoviePy 2.x imports
try:
    from moviepy import VideoFileClip, CompositeVideoClip, ImageClip
except ImportError:
    # Fallback for older moviepy versions
    from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logging_config import get_logger
import config

logger = get_logger(__name__)


class ReelGenerator:
    """Generate vertical Instagram Reels from X/Twitter post URLs."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the ReelGenerator.
        
        Args:
            output_dir: Directory to save output reels. Defaults to config.DOWNLOADS_DIR.
        """
        self.output_dir = Path(output_dir) if output_dir else config.DOWNLOADS_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"ReelGenerator initialized with output directory: {self.output_dir}")
    
    def extract_metadata(self, url: str) -> Dict:
        """
        Extract metadata from X/Twitter post using yt-dlp.
        
        Args:
            url: X/Twitter post URL.
            
        Returns:
            Dictionary containing post metadata.
            
        Raises:
            ValueError: If URL is invalid or metadata extraction fails.
        """
        logger.info(f"Extracting metadata from URL: {url}")
        
        try:
            # Run yt-dlp to extract metadata
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--skip-download", url],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            # Parse JSON response
            data = json.loads(result.stdout)
            
            # Extract relevant fields
            # Try multiple fields for avatar URL
            avatar_url = (
                data.get("uploader_avatar") or 
                data.get("channel_avatar") or 
                data.get("avatar") or
                data.get("uploader_url", "")  # Fallback to profile URL
            )
            
            # Log what we found for avatar
            logger.info(f"Avatar URL extracted: {avatar_url}")
            logger.info(f"Available data keys: {list(data.keys())[:20]}")  # Log first 20 keys
            
            # Try to get uploader_avatar_url specifically
            if not avatar_url or 'x.com' in avatar_url or 'twitter.com' in avatar_url:
                logger.warning("No direct avatar URL found in metadata, will try alternative methods")
            
            metadata = {
                "username": data.get("uploader_id", "unknown"),
                "display_name": data.get("uploader", "Unknown User"),
                "caption": self._truncate_caption(data.get("description", "")),
                "avatar_url": avatar_url,
                "likes": data.get("like_count", 0) or 0,
                "retweets": data.get("repost_count", 0) or 0,
                "comments": data.get("comment_count", 0) or 0,
                "views": data.get("view_count", 0) or 0,
                "timestamp": self._format_timestamp(data.get("upload_date", "")),
                "post_url": url,
                "post_id": data.get("id", "unknown"),
            }
            
            logger.info(f"Successfully extracted metadata for post {metadata['post_id']}")
            return metadata
            
        except subprocess.CalledProcessError as e:
            error_msg = f"yt-dlp failed: {e.stderr}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse yt-dlp output: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error extracting metadata: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _truncate_caption(self, caption: str) -> str:
        """Truncate caption to maximum length while preserving line breaks."""
        if not caption:
            return ""
        
        if len(caption) <= config.MAX_CAPTION_LENGTH:
            return caption
        
        truncated = caption[:config.MAX_CAPTION_LENGTH].rsplit(' ', 1)[0]
        return truncated + "..."
    
    def _format_timestamp(self, upload_date: str) -> str:
        """Format upload date to readable format like 'Jan 24, 2026'."""
        if not upload_date:
            return datetime.now().strftime("%b %d, %Y")
        
        try:
            # upload_date is in format YYYYMMDD
            dt = datetime.strptime(upload_date, "%Y%m%d")
            return dt.strftime("%b %d, %Y")
        except Exception:
            return datetime.now().strftime("%b %d, %Y")
    
    def prepare_avatar(self, avatar_url: str, username: str = None) -> Optional[Image.Image]:
        """
        Download and prepare circular avatar image with white border.
        
        Args:
            avatar_url: URL of the avatar image or profile URL.
            username: Twitter username (for constructing avatar URL if needed).
            
        Returns:
            PIL Image object or None if download fails.
        """
        logger.info("=" * 60)
        logger.info("AVATAR PREPARATION START")
        logger.info(f"Input avatar_url: {avatar_url}")
        logger.info(f"Input username: {username}")
        
        if not avatar_url:
            logger.warning("No avatar URL provided - skipping avatar")
            logger.info("AVATAR PREPARATION END - NO URL")
            logger.info("=" * 60)
            return None
        
        try:
            # If avatar_url is a profile page URL, try to construct avatar URL from username
            if username and ('x.com' in avatar_url or 'twitter.com' in avatar_url or not avatar_url.startswith('http')):
                logger.info("Profile URL detected, attempting to construct direct avatar URL")
                # Twitter/X avatar pattern: https://unavatar.io/twitter/{username}
                # Alternative: https://avatar.vercel.app/twitter/{username}
                constructed_urls = [
                    f"https://unavatar.io/twitter/{username}",
                    f"https://avatar.vercel.app/twitter/{username}",
                ]
                
                for attempt_url in constructed_urls:
                    logger.info(f"Trying constructed URL: {attempt_url}")
                    try:
                        response = requests.get(attempt_url, timeout=10)
                        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                            avatar_url = attempt_url
                            logger.info(f"Successfully found avatar at: {attempt_url}")
                            break
                    except Exception as e:
                        logger.warning(f"Failed to fetch from {attempt_url}: {e}")
                        continue
                else:
                    logger.warning("Could not construct valid avatar URL, will try original URL")
            
            logger.info(f"Downloading avatar from: {avatar_url}")
            response = requests.get(avatar_url, timeout=10, stream=True)
            response.raise_for_status()
            
            logger.info(f"Avatar download response: {response.status_code}")
            logger.info(f"Content-Type: {response.headers.get('content-type')}")
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                logger.error(f"URL did not return an image, got content-type: {content_type}")
                logger.info("AVATAR PREPARATION END - NOT AN IMAGE")
                logger.info("=" * 60)
                return None
            
            # Open image from response
            logger.info("Opening image from response stream...")
            avatar = Image.open(response.raw)
            logger.info(f"Image opened successfully - size: {avatar.size}, mode: {avatar.mode}")
            
            # Convert to RGB if necessary
            if avatar.mode not in ('RGB', 'RGBA'):
                logger.info(f"Converting image from {avatar.mode} to RGB")
                avatar = avatar.convert('RGB')
            
            # Resize to target size
            size = config.AVATAR_SIZE
            logger.info(f"Resizing avatar to {size}x{size}")
            avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
            
            # Create circular mask
            logger.info("Creating circular mask...")
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # Create output image with transparency
            logger.info("Applying circular mask...")
            output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            if avatar.mode == 'RGBA':
                output.paste(avatar, (0, 0))
            else:
                output.paste(avatar.convert('RGBA'), (0, 0))
            output.putalpha(mask)
            
            # Add white border
            border_size = size + config.AVATAR_BORDER_WIDTH * 2
            logger.info(f"Adding white border - final size: {border_size}x{border_size}")
            bordered = Image.new('RGBA', (border_size, border_size), (255, 255, 255, 255))
            
            # Draw white circle
            draw = ImageDraw.Draw(bordered)
            draw.ellipse((0, 0, border_size, border_size), fill=(255, 255, 255, 255))
            
            # Paste avatar on top
            offset = config.AVATAR_BORDER_WIDTH
            bordered.paste(output, (offset, offset), output)
            
            logger.info("✓ Avatar prepared successfully!")
            logger.info("AVATAR PREPARATION END - SUCCESS")
            logger.info("=" * 60)
            return bordered
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading avatar: {e}")
            logger.info("AVATAR PREPARATION END - NETWORK ERROR")
            logger.info("=" * 60)
            return None
        except Exception as e:
            logger.error(f"Failed to prepare avatar: {e}", exc_info=True)
            logger.info("AVATAR PREPARATION END - EXCEPTION")
            logger.info("=" * 60)
            return None
    
    def download_video(self, url: str, resolution: str = "720p") -> Optional[str]:
        """
        Download video from X/Twitter post using yt-dlp with specified resolution.
        
        Args:
            url: X/Twitter post URL.
            resolution: Desired resolution (360p, 480p, 720p, 1080p).
            
        Returns:
            Path to downloaded video file or None if download fails.
        """
        logger.info(f"Downloading video from: {url} in {resolution}")
        
        # Map resolution to height
        resolution_map = {
            "360p": "360",
            "480p": "480",
            "720p": "720",
            "1080p": "1080"
        }
        max_height = resolution_map.get(resolution, "720")
        
        try:
            # Create temporary file for video
            temp_video = self.output_dir / f"temp_video_{datetime.now().timestamp()}.mp4"
            
            # Download using yt-dlp with optimized settings
            result = subprocess.run(
                [
                    "yt-dlp",
                    "-f", f"best[ext=mp4][height<={max_height}]/best[ext=mp4]/best",  # Resolution-based
                    "-o", str(temp_video),
                    "--concurrent-fragments", "5",
                    "--retries", "2",
                    url
                ],
                capture_output=True,
                text=True,
                timeout=config.MAX_PROCESSING_TIMEOUT,
                check=True
            )
            
            if temp_video.exists():
                logger.info(f"Video downloaded successfully to: {temp_video}")
                return str(temp_video)
            else:
                logger.error("Video file not found after download")
                return None
                
        except subprocess.CalledProcessError as e:
            error_msg = f"yt-dlp download failed: {e.stderr}"
            logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Unexpected error downloading video: {e}"
            logger.error(error_msg)
            return None
    
    def create_reel(
        self,
        video_path: str,
        avatar_img: Optional[Image.Image],
        metadata: Dict
    ) -> Optional[Path]:
        """
        Create vertical video with Twitter-like overlays.
        
        Args:
            video_path: Path to source video file.
            avatar_img: PIL Image of circular avatar (or None).
            metadata: Dictionary with post metadata.
            
        Returns:
            Path to output reel file or None if creation fails.
        """
        logger.info("Creating video with overlays...")
        
        video_clip = None
        
        try:
            # Load video
            video_clip = VideoFileClip(video_path)
            original_w, original_h = video_clip.size
            duration = video_clip.duration
            
            logger.info(f"Source video: {original_w}x{original_h}, {duration:.2f}s")
            
            # Create solid background (white or black)
            # Use white background
            background_color = (255, 255, 255)  # White. Change to (0, 0, 0) for black
            background_frame = np.full((config.REEL_HEIGHT, config.REEL_WIDTH, 3), background_color, dtype=np.uint8)
            background_clip = ImageClip(background_frame, duration=duration)
            
            # Keep original aspect ratio - resize to fit within frame with horizontal margins
            # Leave 100px margin on each side horizontally
            # Limit to 720p for speed
            horizontal_margin = 100
            available_width = config.REEL_WIDTH - (2 * horizontal_margin)
            
            # Downscale if larger than 720p for faster processing
            video_w, video_h = original_w, original_h
            if video_h > 720:
                scale_down = 720 / video_h
                video_w = int(video_w * scale_down)
                video_h = 720
            
            scale = min(available_width / video_w, config.REEL_HEIGHT / video_h)
            new_w = int(video_w * scale)
            new_h = int(video_h * scale)
            
            # Calculate video position (centered)
            video_x = (config.REEL_WIDTH - new_w) // 2
            video_y = (config.REEL_HEIGHT - new_h) // 2
            
            logger.info(f"Video will be positioned at ({video_x}, {video_y}) with size {new_w}x{new_h}")
            
            resized_video = video_clip.resized((new_w, new_h))
            resized_video = resized_video.with_position((video_x, video_y))
            
            # Create overlay with text and avatar - pass video position info
            overlay = self._create_overlay(avatar_img, metadata, duration, video_x, new_w, video_y)
            
            # Composite background, video and overlay
            final = CompositeVideoClip(
                [background_clip, resized_video, overlay],
                size=(config.REEL_WIDTH, config.REEL_HEIGHT)
            )
            
            # Preserve audio
            if video_clip.audio:
                final = final.with_audio(video_clip.audio)
            
            # Generate output path
            post_id = metadata.get('post_id', 'unknown')
            output_path = self.output_dir / f"reel_{post_id}.mp4"
            
            # Export video with maximum speed optimization
            logger.info(f"Exporting video to: {output_path}")
            try:
                final.write_videofile(
                    str(output_path),
                    codec='libx264',
                    audio_codec='aac',
                    preset='ultrafast',
                    fps=24,
                    threads=8,  # Max threads
                    bitrate='1500k',  # Lower bitrate for speed
                    audio_bitrate='128k',  # Lower audio bitrate
                    ffmpeg_params=[
                        '-tune', 'fastdecode',  # Optimize for fast decoding
                        '-profile:v', 'baseline',  # Fastest profile
                        '-level', '3.0',
                        '-crf', '30',  # Higher CRF = faster encoding
                        '-maxrate', '1500k',
                        '-bufsize', '3000k',
                        '-movflags', '+faststart',
                        '-max_muxing_queue_size', '4096',
                        '-g', '48',  # GOP size
                        '-sc_threshold', '0',  # Disable scene detection
                    ],
                    logger=None,
                    verbose=False,
                    temp_audiofile=str(self.output_dir / f"temp_audio_{post_id}.m4a"),
                    remove_temp=True,
                    write_logfile=False
                )
            except (BrokenPipeError, IOError, OSError) as e:
                logger.warning(f"Error during video export: {e}, retrying without audio...")
                final_no_audio = final.without_audio()
                final_no_audio.write_videofile(
                    str(output_path),
                    codec='libx264',
                    preset='ultrafast',
                    fps=24,
                    threads=8,
                    bitrate='1500k',
                    ffmpeg_params=[
                        '-tune', 'fastdecode',
                        '-profile:v', 'baseline',
                        '-crf', '30',
                        '-movflags', '+faststart',
                        '-max_muxing_queue_size', '4096',
                        '-g', '48',
                        '-sc_threshold', '0',
                    ],
                    logger=None,
                    verbose=False,
                    write_logfile=False
                )
            
            logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            return None
            
        finally:
            # Cleanup
            if video_clip:
                video_clip.close()
            
            # Remove temporary video file
            try:
                Path(video_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to delete temp video: {e}")
    
    def _create_blurred_background(self, frame: np.ndarray) -> np.ndarray:
        """Create blurred background from video frame."""
        # Convert to PIL Image
        img = Image.fromarray(frame)
        
        # Resize to target resolution
        img = img.resize((config.REEL_WIDTH, config.REEL_HEIGHT), Image.Resampling.LANCZOS)
        
        # Apply Gaussian blur
        img = img.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Darken slightly
        enhancer = Image.new('RGBA', img.size, (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), enhancer)
        
        return np.array(img)
    
    def _create_overlay(
        self,
        avatar_img: Optional[Image.Image],
        metadata: Dict,
        duration: float,
        video_x: int = 80,
        video_w: int = 900,
        video_y: int = 400
    ) -> ImageClip:
        """Create clean text overlay - TweeTakulu screenshot style."""
        # Create transparent overlay
        overlay = Image.new('RGBA', (config.REEL_WIDTH, config.REEL_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load fonts - Linux/Railway compatible
        try:
            # Try DejaVu fonts (available on most Linux systems including Railway)
            display_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
            username_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            caption_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            metrics_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except Exception:
            try:
                # Fallback to Liberation fonts
                display_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 26)
                username_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 22)
                caption_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 28)
                metrics_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 20)
            except Exception:
                # Last resort: use PIL's improved default with size
                logger.warning("Could not load system fonts, using PIL default")
                from PIL import ImageFont
                display_font = ImageFont.load_default()
                username_font = display_font
                caption_font = display_font
                metrics_font = display_font
        
        # Text colors for white background
        text_color = (0, 0, 0, 255)  # Black
        gray_text_color = (120, 120, 120, 255)
        
        # Position elements relative to video position
        # Avatar is above the video, aligned with left edge of video
        avatar_margin_above_caption = 20
        caption_margin_above_video = 30
        
        # Calculate caption height based on text length (estimate)
        caption_text = metadata.get('caption', '')
        estimated_lines = max(1, len(caption_text) // 50)  # Rough estimate
        caption_height = estimated_lines * 38  # 38px per line
        
        # Caption position - just above the video, with space for multiline
        caption_y = video_y - caption_margin_above_video - caption_height
        caption_x = video_x
        
        # Avatar position - just above the caption
        avatar_y = caption_y - config.AVATAR_SIZE - config.AVATAR_BORDER_WIDTH * 2 - avatar_margin_above_caption
        avatar_x = video_x
        
        # Draw avatar if available
        if avatar_img:
            logger.info(f"Pasting avatar at position ({avatar_x}, {avatar_y})")
            overlay.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
            # Text next to avatar
            text_x = avatar_x + config.AVATAR_SIZE + config.AVATAR_BORDER_WIDTH * 2 + 12
            logger.info("Avatar pasted successfully in overlay")
        else:
            # If no avatar, just show text at avatar position
            text_x = avatar_x
            logger.warning("No avatar image available - skipping avatar in overlay")
        
        # Display name (bold)
        draw.text((text_x, avatar_y + 5), metadata['display_name'], 
                 fill=text_color, font=display_font)
        
        # Username below display name (gray)
        username_text = f"@{metadata['username']}"
        draw.text((text_x, avatar_y + 35), username_text, 
                 fill=gray_text_color, font=username_font)
        
        # Caption - positioned just above video, spanning video width
        caption_text = metadata.get('caption', '')
        if caption_text:
            # Multi-line caption support
            self._draw_multiline_text(
                draw,
                caption_text,
                (caption_x, caption_y),
                caption_font,
                text_color,
                video_w  # Caption width matches video width
            )
        
        # BOTTOM - Only timestamp (below video)
        if metadata.get('timestamp'):
            bottom_y = config.REEL_HEIGHT - 100
            draw.text((video_x, bottom_y), metadata['timestamp'], 
                     fill=gray_text_color, font=metrics_font)
        
        # Convert to numpy array and create ImageClip
        overlay_array = np.array(overlay)
        return ImageClip(overlay_array, duration=duration)
    
    def _draw_multiline_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.ImageFont,
        fill: Tuple[int, int, int, int],
        max_width: int
    ):
        """Draw multiline text with word wrapping."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines with better spacing
        x, y = position
        line_height = 38  # Increased for better readability
        for i, line in enumerate(lines[:6]):  # Max 6 lines
            if line.strip():  # Only draw non-empty lines
                draw.text((x, y), line, fill=fill, font=font)
                y += line_height
    
    def _format_count(self, count: int) -> str:
        """Format count with K notation for thousands."""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        else:
            return str(count)
    
    def create_reel_from_url(self, url: str, resolution: str = "720p") -> Tuple[Optional[Path], dict]:
        """
        Main orchestration method to create reel from X/Twitter URL.
        
        Args:
            url: X/Twitter post URL.
            resolution: Desired resolution (360p, 480p, 720p, 1080p).
            
        Returns:
            Tuple of (output_path, metadata) or (None, error_message).
        """
        logger.info(f"Starting reel creation for URL: {url} with resolution: {resolution}")
        
        try:
            # Step 1: Extract metadata
            metadata = self.extract_metadata(url)
            
            # Step 2: Prepare avatar
            avatar_img = self.prepare_avatar(metadata['avatar_url'], metadata.get('username'))
            
            # Step 3: Download video with resolution
            video_path = self.download_video(url, resolution=resolution)
            if not video_path:
                return None, {"error": "Failed to download video"}
            
            # Step 4: Create reel
            output_path = self.create_reel(video_path, avatar_img, metadata)
            
            if output_path:
                return output_path, metadata
            else:
                return None, {"error": "Failed to create reel"}
                
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"ValueError during reel creation: {error_msg}")
            return None, {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Exception during reel creation: {error_msg}")
            return None, {"error": error_msg}
