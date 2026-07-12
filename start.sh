#!/bin/bash

echo "🧬 Starting Myntra Identity Full-Stack App..."

# Kill any existing processes on ports 8000 and 5173
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start the Backend in the background
echo "🚀 Starting Python FastAPI Backend on port 8000..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start the Frontend
echo "✨ Starting React Vite Frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Both servers are running!"
echo "👉 Backend: http://localhost:8000"
echo "👉 Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both servers."

# Wait for user to press Ctrl+C, then kill both servers
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
