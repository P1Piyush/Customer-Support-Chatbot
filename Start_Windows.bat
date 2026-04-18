@echo off
echo 🤖 Starting Chatbot Demo...

REM Move to the directory where this script is located
cd /d "%~dp0"

REM Check if streamlit is installed. If not, install dependencies automatically.
python -c "import streamlit" >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 First time setup: Installing dependencies...
    pip install -r requirements.txt
)

echo 🚀 Booting up Streamlit server...
python -m streamlit run app.py

pause
