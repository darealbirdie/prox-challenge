#!/bin/bash
# Quick launch script for React frontend + backend

echo "🚀 Launching Claude Welding Agent React Frontend..."
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install flask flask-cors -q

# Create a simple package.json if needed
if [ ! -f "welding-agent-frontend/package.json" ]; then
    echo "⚠️  React app not found!"
    echo "Creating minimal setup..."
    mkdir -p welding-agent-frontend/public
    cat > welding-agent-frontend/package.json << 'PKG'
{
  "name": "welding-agent-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "react-markdown": "^8.0.7"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {"production": [">0.2%"], "development": ["last 1 chrome version"]}
}
PKG
fi

# Start backend in background
echo "🔧 Starting Flask backend..."
python backend.py &
BACKEND_PID=$!
sleep 3

# Check if backend is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend running on http://localhost:5000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🌐 Starting React frontend..."
cd welding-agent-frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "======================================================================"
echo "✅ Everything is running!"
echo "======================================================================"
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "API Docs: curl http://localhost:5000/api/health"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "======================================================================"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
