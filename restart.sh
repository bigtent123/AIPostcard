#!/bin/bash

# Kill any existing processes on ports 9000, 9001 and 3020
echo "Stopping any existing servers..."

# More aggressive process killing to avoid port conflicts
for PORT in 9000 9001 3020
do
    # Find and kill processes using these ports
    PID=$(lsof -ti:$PORT)
    if [ ! -z "$PID" ]; then
        echo "Killing process $PID on port $PORT"
        kill -9 $PID 2>/dev/null || echo "Failed to kill process on port $PORT"
        # Give it a moment to fully release the port
        sleep 1
    else
        echo "No process found on port $PORT"
    fi
done

# Clear any existing Python processes related to the app
ps aux | grep "python.*app.main" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# Start the backend
echo "Starting backend on port 9001..."
cd /Users/shane/Documents/Postcard\ Website/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9001 --reload &
BACKEND_PID=$!

# Wait a moment for the backend to initialize
sleep 3

# Start the frontend on port 3021
echo "Starting frontend on port 3021..."
cd /Users/shane/Documents/Postcard\ Website/frontend
npm run dev -- --port 3021 &
FRONTEND_PID=$!

echo "Servers started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend running on: http://localhost:9001"
echo "Frontend running on: http://localhost:3021"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to press Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped'; exit 0" SIGINT
wait
