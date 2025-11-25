#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template. Please configure your API keys."
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏦 K-BANK Metadata AI Platform 개발환경 시작${NC}"
echo -e "${BLUE}===========================================${NC}"

# Function to start services
start_backend() {
    echo -e "${YELLOW}Starting FastAPI backend...${NC}"
    cd backend
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo -e "${GREEN}✓ Backend started with PID: $BACKEND_PID${NC}"
}

start_frontend() {
    echo -e "${YELLOW}Starting React frontend...${NC}"
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    npm start &
    FRONTEND_PID=$!
    cd ..
    echo -e "${GREEN}✓ Frontend started with PID: $FRONTEND_PID${NC}"
}

# Start services
echo ""
start_backend
sleep 3
start_frontend

echo ""
echo -e "${GREEN}✅ All services are starting up...${NC}"
echo ""
echo -e "${BLUE}📊 Access the applications at:${NC}"
echo -e "   ${GREEN}React Dashboard:${NC} http://localhost:3000"
echo -e "   ${GREEN}FastAPI Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait and handle shutdown
trap cleanup INT

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

# Keep script running
wait