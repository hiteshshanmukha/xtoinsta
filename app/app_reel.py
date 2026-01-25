"""Flask API for X to Instagram Reel Converter."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from app.reel_generator import ReelGenerator
from logging_config import get_logger
import config

logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize reel generator
reel_generator = ReelGenerator()


@app.route('/', methods=['GET'])
def index():
    """Health check endpoint."""
    return jsonify({
        "service": "x-to-reel-converter",
        "status": "ok",
        "version": "1.0.0"
    })


@app.route('/api/create-reel', methods=['POST'])
def create_reel():
    """
    Create an Instagram Reel from X/Twitter post URL.
    
    Request body:
        {
            "url": "https://x.com/username/status/1234567890"
        }
    
    Returns:
        Success: 200 with reel metadata and filename
        Error: 4xx/5xx with error message
    """
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        url = data.get('url')
        resolution = data.get('resolution', '720p')  # Default to 720p
        if not url:
            return jsonify({"error": "Missing 'url' field in request"}), 400
        
        # Validate URL format
        if not (url.startswith('https://x.com/') or url.startswith('https://twitter.com/')):
            return jsonify({"error": "Invalid X/Twitter URL format"}), 400
        
        logger.info(f"Received create-reel request for URL: {url} with resolution: {resolution}")
        
        # Create reel with resolution parameter
        output_path, metadata = reel_generator.create_reel_from_url(url, resolution=resolution)
        
        if output_path is None:
            error_msg = metadata.get('error', 'Unknown error occurred')
            logger.error(f"Reel creation failed: {error_msg}")
            return jsonify({"error": error_msg}), 500
        
        # Get file info
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        filename = output_path.name
        
        # Prepare response
        response = {
            "success": True,
            "post_id": metadata.get('post_id', 'unknown'),
            "username": metadata.get('username', 'unknown'),
            "file": filename,
            "message": "Reel created successfully",
            "metadata": {
                "username": metadata.get('username'),
                "display_name": metadata.get('display_name'),
                "likes": metadata.get('likes'),
                "retweets": metadata.get('retweets'),
                "comments": metadata.get('comments'),
                "views": metadata.get('views'),
                "caption": metadata.get('caption'),
                "timestamp": metadata.get('timestamp'),
                "file_size_mb": round(file_size_mb, 2)
            }
        }
        
        logger.info(f"Reel created successfully: {filename}")
        return jsonify(response), 200
        
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500


@app.route('/api/download-reel/<filename>', methods=['GET'])
def download_reel(filename):
    """
    Download a generated reel file.
    
    Args:
        filename: Name of the reel file (e.g., 'reel_1234567890.mp4')
    
    Returns:
        The MP4 file or 404 if not found
    """
    try:
        # Validate filename (security: prevent directory traversal)
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"error": "Invalid filename"}), 400
        
        if not filename.endswith('.mp4'):
            return jsonify({"error": "Only MP4 files can be downloaded"}), 400
        
        file_path = config.DOWNLOADS_DIR / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {filename}")
            return jsonify({"error": "File not found"}), 404
        
        logger.info(f"Serving file: {filename}")
        return send_file(
            file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        error_msg = f"Error downloading file: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500


if __name__ == '__main__':
    logger.info(f"Starting Flask API on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
