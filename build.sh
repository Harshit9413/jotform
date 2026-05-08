#!/usr/bin/env bash
set -e

echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🏗️  Building React frontend..."
VITE_APP_URL="${VITE_APP_URL}" npm run build

echo "🐍 Installing backend dependencies..."
cd ../backend
pip install -r requirements.txt

echo "✅ Build complete!"
