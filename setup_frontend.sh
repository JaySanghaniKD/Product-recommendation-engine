#!/bin/bash

# Exit on any error
set -e

echo "⚛️ Setting up React frontend..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing npm dependencies..."
npm install

echo "✅ Frontend setup complete."
echo "To start the frontend development server, run:"
echo "cd frontend"
echo "npm start"
