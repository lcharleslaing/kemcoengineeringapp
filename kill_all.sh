#!/bin/bash

echo "========================================="
echo "Killing all Django and Electron processes"
echo "========================================="

# Kill all Django processes
echo "Killing Django processes..."
pkill -9 -f "manage.py runserver" 2>/dev/null
pkill -9 -f "python.*manage.py" 2>/dev/null
pkill -9 -f "django" 2>/dev/null

# Kill all Electron processes
echo "Killing Electron processes..."
pkill -9 -f "electron" 2>/dev/null
pkill -9 -f "Electron" 2>/dev/null

# Kill processes on port 8001 (Windows compatible)
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:8001 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Killing process $PID on port 8001..."
        kill -9 $PID 2>/dev/null
    fi
fi

# Windows-specific cleanup
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WINDIR" ]]; then
    echo "Windows cleanup..."
    taskkill /F /IM electron.exe 2>/dev/null || true
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *manage.py*" 2>/dev/null || true
    netstat -ano | findstr :8001 | awk '{print $5}' | xargs -I {} taskkill /F /PID {} 2>/dev/null || true
fi

echo "✓ Cleanup complete"
echo "========================================="

