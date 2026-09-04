#!/bin/bash
set -e
echo "🚀 [1/4] Preparing NeuroStudy Production Build..."
docker build -t neurostudy:latest .
echo "📦 [2/4] Starting Docker Compose with Volume Persistence..."
docker compose up -d
echo "🩺 [3/4] Running Service Health Check..."
sleep 5
curl -f http://localhost:8501/_stcore/health && echo "✓ Streamlit Frontend Healthy!"
curl -f http://localhost:8000/api/health && echo "✓ FastAPI Backend Healthy!"
echo "🌐 [4/4] NeuroStudy Production Engine is LIVE!"
