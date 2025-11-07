#!/bin/bash

# Django startup script for leecharleslaingdotnet Electron app
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Starting Django from: $SCRIPT_DIR"
echo "========================================="

# Django server port - change this if you need a different port
DJANGO_PORT=8001

# Kill any existing Django servers on port (multiple methods for reliability)
echo "Cleaning up port $DJANGO_PORT..."

# Method 1: Kill by process name
pkill -9 -f "manage.py runserver" 2>/dev/null

# Method 2: Kill by port using lsof
PID=$(lsof -ti:$DJANGO_PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Killing process $PID on port $DJANGO_PORT..."
    kill -9 $PID 2>/dev/null
fi

# Method 3: Alternative using fuser
fuser -k $DJANGO_PORT/tcp 2>/dev/null

# Wait a moment for cleanup
sleep 1

# Verify port is free
if lsof -Pi :$DJANGO_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "ERROR: Port $DJANGO_PORT is still in use!"
    echo "Please manually stop the process:"
    lsof -i :$DJANGO_PORT
    exit 1
fi

echo "✓ Port $DJANGO_PORT is free"

# Activate Python environment (conda or venv)
# Try conda first (for Linux/home setup)
ENV_ACTIVATED=false

echo "📦 Activating Python environment..."

# Try to activate conda environment
CONDA_ACTIVATED=false
if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
    CONDA_ACTIVATED=true
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    CONDA_ACTIVATED=true
elif [ -f "/c/Users/$USER/anaconda3/etc/profile.d/conda.sh" ]; then
    source "/c/Users/$USER/anaconda3/etc/profile.d/conda.sh"
    CONDA_ACTIVATED=true
elif [ -f "/c/Users/$USER/miniconda3/etc/profile.d/conda.sh" ]; then
    source "/c/Users/$USER/miniconda3/etc/profile.d/conda.sh"
    CONDA_ACTIVATED=true
elif [ -f "$HOME/AppData/Local/Continuum/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/AppData/Local/Continuum/anaconda3/etc/profile.d/conda.sh"
    CONDA_ACTIVATED=true
elif [ -f "$HOME/AppData/Local/Continuum/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/AppData/Local/Continuum/miniconda3/etc/profile.d/conda.sh"
    CONDA_ACTIVATED=true
elif command -v conda &> /dev/null; then
    # Conda is in PATH but conda.sh not found
    CONDA_ACTIVATED=true
fi

if [ "$CONDA_ACTIVATED" = true ]; then
    # Try kemco first (home Linux setup), then django (work Windows setup), then venv
    if conda activate kemco 2>/dev/null; then
        echo "✓ Activated conda environment: kemco"
        ENV_ACTIVATED=true
    elif conda activate django 2>/dev/null; then
        echo "✓ Activated conda environment: django"
        ENV_ACTIVATED=true
    else
        echo "⚠️  Conda found but 'kemco' or 'django' environment not found, trying venv..."
    fi
fi

# If conda didn't work, try Python venv (for Windows/work setup)
if [ "$ENV_ACTIVATED" = false ]; then
    # Common venv directory names
    VENV_DIRS=("venv" ".venv" "env" "ENV")
    
    # Detect OS for venv activation script path
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WINDIR" ]]; then
        # Windows (Git Bash)
        ACTIVATE_SCRIPT="Scripts/activate"
    else
        # Linux/Mac
        ACTIVATE_SCRIPT="bin/activate"
    fi
    
    for venv_dir in "${VENV_DIRS[@]}"; do
        if [ -f "$venv_dir/$ACTIVATE_SCRIPT" ]; then
            echo "✓ Found venv at: $venv_dir"
            source "$venv_dir/$ACTIVATE_SCRIPT"
            ENV_ACTIVATED=true
            break
        fi
    done
fi

# Verify Python environment is working
if [ "$ENV_ACTIVATED" = true ]; then
    if python -c "import django" 2>/dev/null; then
        echo "✓ Django is available in Python environment"
    else
        echo "⚠️  Warning: Django not found in current Python environment"
        echo "   Continuing anyway - Django may be installed globally or in PATH"
    fi
else
    echo "⚠️  Warning: Could not activate conda or venv"
    echo "   Using system Python (make sure Django is installed)"
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        echo "❌ Error: Python not found. Please install Python or activate your environment."
        exit 1
    fi
fi

# Ensure we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found in $SCRIPT_DIR"
    exit 1
fi

echo "✓ Project directory verified"
echo "Starting Django development server on port $DJANGO_PORT..."
echo "========================================="

# Start Django server
python manage.py runserver $DJANGO_PORT