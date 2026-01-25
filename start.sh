#!/bin/bash
# Start Flask API in background
python app/app_reel.py &

# Wait for Flask to start
sleep 5

# Start Streamlit
streamlit run streamlit_ui/app_reel.py --server.port=${PORT:-8501} --server.address=0.0.0.0
