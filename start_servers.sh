#!/bin/bash

echo "=================================================="
echo "🧋 BOBA BI - Starting Servers"
echo "=================================================="
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not set in environment"
    echo "   The API key in boba_bi.py will be used"
    echo ""
fi

# Kill any existing servers
echo "🔄 Cleaning up existing servers..."
pkill -f "http.server 8000" 2>/dev/null
pkill -f "api_server.py" 2>/dev/null
sleep 2

# Start API server in background
echo "🚀 Starting API server on port 5000..."
python3 api_server.py > api_server.log 2>&1 &
API_PID=$!
sleep 3

# Check if API server started successfully
if ps -p $API_PID > /dev/null; then
    echo "✅ API server started (PID: $API_PID)"

    # Test API health
    if curl -s http://localhost:5000/ | grep -q "Boba BI API"; then
        echo "✅ API server is healthy"
    else
        echo "❌ API server not responding correctly"
        exit 1
    fi
else
    echo "❌ Failed to start API server"
    cat api_server.log
    exit 1
fi

# Start frontend server in background
echo "🌐 Starting frontend server on port 8000..."
python3 -m http.server 8000 > frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 2

# Check if frontend server started successfully
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Frontend server started (PID: $FRONTEND_PID)"
else
    echo "❌ Failed to start frontend server"
    cat frontend.log
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ ALL SERVERS RUNNING"
echo "=================================================="
echo ""
echo "📊 API Server:"
echo "   URL: http://localhost:5000"
echo "   Logs: tail -f api_server.log"
echo ""
echo "🌐 Frontend Server:"
echo "   URL: http://localhost:8000/demo_frontend.html"
echo "   Logs: tail -f frontend.log"
echo ""
echo "🔧 In VS Code/Codespaces:"
echo "   1. Open PORTS panel"
echo "   2. Make ports 5000 and 8000 PUBLIC"
echo "   3. Click 'Open in Browser' for port 8000"
echo "   4. Add /demo_frontend.html to the URL"
echo ""
echo "🛑 To stop servers:"
echo "   pkill -f 'http.server 8000'"
echo "   pkill -f 'api_server.py'"
echo ""
echo "📝 Troubleshooting: See TROUBLESHOOTING.md"
echo "=================================================="
echo ""

# Keep script running and show logs
echo "Press Ctrl+C to stop servers and exit..."
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

trap cleanup INT TERM

# Tail logs
tail -f api_server.log frontend.log
