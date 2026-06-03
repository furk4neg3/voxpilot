#!/bin/bash
# VoxPilot Streamlit UI
set -e
echo "🖥️ Starting VoxPilot Streamlit UI..."
streamlit run ui/streamlit_app.py --server.port 8501
