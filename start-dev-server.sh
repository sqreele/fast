#!/bin/bash

echo "🚀 Starting PM System Development Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill any existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f uvicorn || true
pkill -f "next dev" || true

# Start Backend
echo -e "${YELLOW}🐍 Starting Backend Server...${NC}"
cd backend

# Install dependencies if needed
if [ ! -f "/home/ubuntu/.local/lib/python3.13/site-packages/fastapi/__init__.py" ]; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    python3 -m pip install --break-system-packages -r requirements-minimal.txt email-validator sqladmin
fi

# Start the backend server in background
export PATH=$PATH:/home/ubuntu/.local/bin
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Backend server started successfully${NC}"
        break
    fi
    sleep 1
done

# Check if backend is actually running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}❌ Backend server failed to start. Check backend.log for errors${NC}"
    cat backend.log | tail -20
    exit 1
fi

# Start Frontend
echo -e "${YELLOW}⚛️ Starting Frontend Server...${NC}"
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

# Start the frontend server in background
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ Frontend server started successfully${NC}"
        break
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}🎉 Development servers are running!${NC}"
echo ""
echo -e "${YELLOW}📋 Access URLs:${NC}"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Backend Health: http://localhost:8000/health"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}📁 Log Files:${NC}"
echo "   Backend: backend/backend.log"
echo "   Frontend: frontend/frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop servers:${NC}"
echo "   pkill -f uvicorn"
echo "   pkill -f \"next dev\""
echo ""
echo "Process IDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"