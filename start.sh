#!/bin/bash
# Set API URL for internal communication
export API_URL="http://127.0.0.1:5000"

# Start Flask API in background
python app/app_reel.py &

# Store Flask PID
FLASK_PID=$!

# Wait for Flask to start and verify it's running
echo "Waiting for Flask API to start..."
sleep 3

# Check if Flask is running
for i in {1..10}; do
  if curl -s http://127.0.0.1:5000/ > /dev/null; then
    echo "Flask API is ready!"
    break
  fi
  echo "Waiting for Flask... attempt $i/10"
  sleep 2
done

# Start Streamlit on Railway's PORT
echo "Starting Streamlit on port ${PORT:-8501}..."
streamlit run streamlit_ui/app_reel.py --server.port=${PORT:-8501} --server.address=0.0.0.0
