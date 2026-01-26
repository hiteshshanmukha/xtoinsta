#!/bin/bash
set -e  # Exit on error

echo "=== Starting X to Instagram Converter ==="

# Start Flask API in background
echo "Starting Flask API on port 5000..."
python app/app_reel.py &
FLASK_PID=$!
echo "Flask PID: $FLASK_PID"

# Wait for Flask to be ready
echo "Waiting for Flask API to start..."
sleep 5

# Verify Flask is running
for i in {1..15}; do
  if curl -f http://127.0.0.1:5000/ > /dev/null 2>&1; then
    echo "✓ Flask API is ready!"
    break
  fi
  echo "⏳ Waiting for Flask... attempt $i/15"
  sleep 2
done

# Check if Flask actually started
if ! curl -f http://127.0.0.1:5000/ > /dev/null 2>&1; then
  echo "❌ Flask API failed to start!"
  exit 1
fi

# Export API URL for Streamlit
export API_URL="http://127.0.0.1:5000"
echo "API_URL set to: $API_URL"

# Start Streamlit on Railway's PORT
echo "Starting Streamlit on port ${PORT:-8501}..."
exec streamlit run streamlit_ui/app_reel.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true
