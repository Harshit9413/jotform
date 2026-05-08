#!/bin/bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Activate virtualenv
source "$ROOT/myvenv/bin/activate"

mkdir -p "$ROOT/logs"

echo "Starting Backend   → http://localhost:8000"
echo "Starting Frontend  → http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all."
echo ""

# Start unified backend
cd "$ROOT/backend" && uvicorn main:app --reload --port 8000 > "$ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!

# Start frontend
cd "$ROOT/frontend" && npm run dev > "$ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!

trap "echo ''; echo 'Stopping all...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait
