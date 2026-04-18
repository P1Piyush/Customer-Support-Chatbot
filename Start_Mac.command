#!/bin/bash
# Move to the directory where this script is located
cd "$(dirname "$0")"

echo "🤖 Starting Chatbot Demo..."

# Check if streamlit is installed. If not, install dependencies automatically.
python3 -c "import streamlit" 2>/dev/null || {
    echo "📦 First time setup: Installing dependencies..."
    # We use --break-system-packages to bypass Apple's PEP 668 protection
    python3 -m pip install -r requirements.txt --break-system-packages
}

echo "🚀 Booting up Streamlit server..."

# Instruct macOS to open Brave Browser automatically in 3 seconds
(sleep 3 && open -a "Brave Browser" "http://localhost:8501" 2>/dev/null || open "http://localhost:8501") &

# Run Streamlit in the foreground, but stop it from opening Safari
python3 -m streamlit run app.py --server.headless true
