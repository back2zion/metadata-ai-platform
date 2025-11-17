#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template. Please configure your API keys."
fi

# Function to start services
start_backend() {
    echo "Starting FastAPI backend..."
    cd backend
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "Backend started with PID: $BACKEND_PID"
}

start_streamlit() {
    echo "Starting Streamlit frontend..."
    streamlit run app.py --server.port 8501 &
    STREAMLIT_PID=$!
    echo "Streamlit started with PID: $STREAMLIT_PID"
}

# Start services
echo "🏥 Starting Seoul Asan Hospital IDP POC..."
echo "=" * 50

start_backend
sleep 3
start_streamlit

echo ""
echo "✅ Services are starting up..."
echo ""
echo "📊 Access the applications at:"
echo "   - Streamlit Dashboard: http://localhost:8501"
echo "   - FastAPI Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and handle shutdown
trap "echo 'Shutting down...'; kill $BACKEND_PID $STREAMLIT_PID; exit" INT
wait