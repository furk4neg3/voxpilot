#!/bin/bash
# VoxPilot API Server
set -e
echo "🎙️ Starting VoxPilot API Server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
