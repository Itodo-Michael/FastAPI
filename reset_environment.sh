#!/bin/bash

echo "🔄 Resetting environment..."

# Remove broken environment
deactivate 2>/dev/null
rm -rf venv

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo apt update
sudo apt install python3.11 python3.11-venv -y

# Create environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
echo "📦 Installing packages..."
pip install -r requirements.txt

echo "✅ Environment ready with Python 3.11"
echo "🚀 Run: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
