#!/bin/bash

# Script to forcefully clean up port 8000
echo "Cleaning up port 8000..."

# Kill all Django runserver processes
pkill -9 -f "manage.py runserver" 2>/dev/null

# Kill anything on port 8000
PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Killing process(es): $PID"
    kill -9 $PID 2>/dev/null
fi

# Alternative method
fuser -k 8000/tcp 2>/dev/null

# Wait and verify
sleep 1

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  WARNING: Port 8000 is still in use!"
    lsof -i :8000
    exit 1
else
    echo "✓ Port 8000 is now free"
    exit 0
fi

