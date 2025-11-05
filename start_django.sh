#!/bin/bash

# Django startup script for leecharleslaingdotnet Electron app
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Starting Django from: $SCRIPT_DIR"
echo "========================================="

# Kill any existing Django servers on port 8000 (multiple methods for reliability)
echo "Cleaning up port 8000..."

# Method 1: Kill by process name
pkill -9 -f "manage.py runserver" 2>/dev/null

# Method 2: Kill by port using lsof
PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Killing process $PID on port 8000..."
    kill -9 $PID 2>/dev/null
fi

# Method 3: Alternative using fuser
fuser -k 8000/tcp 2>/dev/null

# Wait a moment for cleanup
sleep 1

# Verify port is free
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "ERROR: Port 8000 is still in use!"
    echo "Please manually stop the process:"
    lsof -i :8000
    exit 1
fi

echo "✓ Port 8000 is free"

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
    if conda activate django 2>/dev/null; then
        echo "✓ Activated conda environment: django"
        ENV_ACTIVATED=true
    else
        echo "⚠️  Conda found but 'django' environment not found, trying venv..."
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
echo "Starting Django development server on port 8000..."
echo "========================================="

# Start Django server
python manage.py runserver 8000