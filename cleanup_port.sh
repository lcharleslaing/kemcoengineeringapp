#!/bin/bash

# Django server port - change this if you need a different port
DJANGO_PORT=8001

# Script to forcefully clean up Django port
echo "Cleaning up port $DJANGO_PORT..."

# Kill all Django runserver processes
pkill -9 -f "manage.py runserver" 2>/dev/null

# Kill anything on port
PID=$(lsof -ti:$DJANGO_PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Killing process(es): $PID"
    kill -9 $PID 2>/dev/null
fi

# Alternative method
fuser -k $DJANGO_PORT/tcp 2>/dev/null

# Wait and verify
sleep 1

if lsof -Pi :$DJANGO_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  WARNING: Port $DJANGO_PORT is still in use!"
    lsof -i :$DJANGO_PORT
    exit 1
else
    echo "✓ Port $DJANGO_PORT is now free"
    exit 0
fi

