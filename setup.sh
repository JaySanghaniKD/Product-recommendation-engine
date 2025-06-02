#!/bin/bash

# Exit on any error
set -e

echo "📦 Setting up AI E-commerce Project..."

# Check if required tools are installed
echo "🔍 Checking prerequisites..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Check for pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✅ Prerequisites check passed."

# Setup backend
echo "🔧 Setting up backend..."
./setup_backend.sh

# Setup frontend
echo "🔧 Setting up frontend..."
./setup_frontend.sh

echo "🎉 Setup complete! You can now start the application."
echo "📘 See README.md for instructions on how to start the servers."
