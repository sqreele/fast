#!/bin/bash

# Start Services Script
# This script helps start the frontend and backend services

set -e

echo "🚀 Starting Property Management System Services..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found - using Docker Compose"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "❌ Error: .env file not found"
        echo "Please create .env file from .env.example"
        exit 1
    fi
    
    # Start services with Docker Compose
    echo "📦 Starting services with Docker Compose..."
    docker-compose up -d
    
    echo "✅ Services started successfully!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    
else
    echo "⚠️  Docker not found - starting services manually"
    
    # Start backend
    echo "🐍 Starting backend service..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    echo "📦 Installing backend dependencies..."
    source venv/bin/activate
    pip install --break-system-packages -r requirements.txt || {
        echo "⚠️  Some dependencies failed to install. Trying to start with available packages..."
    }
    
    # Start backend in background
    echo "🚀 Starting FastAPI backend..."
    python3 main.py &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    
    # Go back to root and start frontend
    cd ../frontend
    
    # Install frontend dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend
    echo "🚀 Starting Next.js frontend..."
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started with PID: $FRONTEND_PID"
    
    echo ""
    echo "✅ Services started successfully!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop services, run: kill $BACKEND_PID $FRONTEND_PID"
fi

echo ""
echo "🎉 Setup complete! You can now access the application."
echo "If you encounter the 'Failed to load profile' error, make sure both services are running."