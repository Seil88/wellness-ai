#!/bin/bash
# Wellness.AI — Start all dev services
# Usage: ./start-dev.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "Shutting down services..."
  kill $WEB_PID $API_PID 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Serve web files on port 8080
echo "Starting web file server on :8080..."
cd "$PROJECT_ROOT"
python3 -m http.server 8080 &
WEB_PID=$!

# 2. Start FastAPI backend on port 8000
echo "Starting FastAPI backend on :8000..."
cd "$PROJECT_ROOT/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# 3. Wait a moment for servers to start
sleep 2
echo ""
echo "Web server:  http://localhost:8080"
echo "API server:  http://localhost:8000"
echo ""

# 4. Build & run Expo iOS app
echo "Building Expo iOS app..."
cd "$PROJECT_ROOT/mobile"
npx expo run:ios --device "iPhone 17 Pro"

# Keep running until Ctrl+C
cleanup
