#!/bin/bash

# Exit on any error
set -e

echo "🐍 Setting up Python backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete."
echo "To start the backend server, run:"
echo "source venv/bin/activate"
echo "uvicorn app.main:app --reload"
