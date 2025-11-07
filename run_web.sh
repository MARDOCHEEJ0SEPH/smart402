#!/bin/bash
# Smart402 Web Dashboard Launcher

echo "========================================"
echo "Smart402 Web Dashboard Launcher"
echo "========================================"
echo ""

# Check if Flask is installed
if ! python -c "import flask" &> /dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Navigate to web directory and start server
echo "Starting Flask server..."
echo "Dashboard will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

cd web && python app.py
