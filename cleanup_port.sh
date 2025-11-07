#!/bin/bash

# Django server port - change this if you need a different port
DJANGO_PORT=8001

# Script to forcefully clean up Django port and Electron processes
echo "========================================="
echo "Cleaning up port $DJANGO_PORT and processes..."
echo "========================================="

# Kill all Django runserver processes
echo "Killing Django processes..."
pkill -9 -f "manage.py runserver" 2>/dev/null
pkill -9 -f "python.*manage.py" 2>/dev/null

# Kill all Electron processes
echo "Killing Electron processes..."
pkill -9 -f "electron" 2>/dev/null
pkill -9 -f "Electron" 2>/dev/null

# Kill anything on port
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:$DJANGO_PORT 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Killing process(es) on port $DJANGO_PORT: $PID"
        kill -9 $PID 2>/dev/null
    fi
fi

# Alternative method
if command -v fuser &> /dev/null; then
    fuser -k $DJANGO_PORT/tcp 2>/dev/null
fi

# Windows-specific cleanup
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WINDIR" ]]; then
    echo "Windows cleanup..."
    taskkill /F /IM electron.exe 2>/dev/null || true
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *manage.py*" 2>/dev/null || true
fi

# Wait and verify
sleep 1

if command -v lsof &> /dev/null; then
    if lsof -Pi :$DJANGO_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  WARNING: Port $DJANGO_PORT is still in use!"
        lsof -i :$DJANGO_PORT
        exit 1
    else
        echo "✓ Port $DJANGO_PORT is now free"
    fi
else
    echo "✓ Cleanup attempted (lsof not available for verification)"
fi

echo "========================================="
exit 0

