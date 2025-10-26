#!/bin/bash
# Boba BI - Quick Start Script
# Run this to get started immediately!

echo "🧋 Boba BI Quick Start"
echo "======================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install anthropic

# Check for API key
echo ""
echo "⚠️  IMPORTANT: You need to set your Anthropic API key!"
echo ""
echo "Option 1: Set environment variable"
echo "  export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
echo ""
echo "Option 2: Edit boba_bi.py line 21"
echo "  ANTHROPIC_API_KEY = 'sk-ant-your-key-here'"
echo ""
echo "Get your API key at: https://console.anthropic.com/"
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ API key not set in environment"
    echo "   Please set it and run again"
    echo ""
else
    echo "✅ API key found in environment"
    echo ""
    
    # Run test
    echo "Running system tests..."
    python3 test_system.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ All tests passed!"
        echo ""
        echo "Ready to generate schedule? Run:"
        echo "  python3 boba_bi.py"
        echo ""
        echo "Or start the web interface:"
        echo "  Terminal 1: python3 api_server.py"
        echo "  Terminal 2: python3 -m http.server 8000"
        echo "  Browser: http://localhost:8000/demo_frontend.html"
    else
        echo ""
        echo "❌ Some tests failed. Please check errors above."
    fi
fi

echo ""
echo "📚 Documentation:"
echo "  - README.md - Full documentation"
echo "  - HACKATHON_GUIDE.md - Demo script & tips"
echo "  - PROJECT_SUMMARY.md - Complete overview"
echo ""
echo "Good luck! 🍀"
