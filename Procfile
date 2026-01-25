web: streamlit run streamlit_ui/app_reel.py --server.port=$PORT --server.address=0.0.0.0
api: gunicorn app.app_reel:app --bind 0.0.0.0:$PORT