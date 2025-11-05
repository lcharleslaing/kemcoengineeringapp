#!/bin/bash

echo "🐍 Django Server Launcher"
echo "========================="
echo ""

# Activate Python environment (conda or venv)
echo "📦 Activating Python environment..."
ENV_ACTIVATED=false

# Try to activate conda environment first
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

# If conda didn't work, try Python venv
if [ "$ENV_ACTIVATED" = false ]; then
    VENV_DIRS=("venv" ".venv" "env" "ENV")
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WINDIR" ]]; then
        ACTIVATE_SCRIPT="Scripts/activate"
    else
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

echo "🔍 Checking Django setup..."

# Check if Django is working
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django not found in conda environment!"
    echo "Please make sure Django is installed in the 'django' conda environment."
    exit 1
fi

echo "✅ Django is ready!"
echo ""

# Check for existing Django processes
EXISTING_PROCESS=$(pgrep -f "python manage.py runserver")
if [ ! -z "$EXISTING_PROCESS" ]; then
    echo "⚠️  Django server is already running (PID: $EXISTING_PROCESS)"
    echo "You can:"
    echo "1. Stop it with: kill $EXISTING_PROCESS"
    echo "2. Or access it at: http://127.0.0.1:8000"
    echo ""
    read -p "Stop existing server and start new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Stopping existing Django server..."
        kill $EXISTING_PROCESS
        sleep 2
    else
        echo "📝 Existing server will continue running at: http://127.0.0.1:8000"
        exit 0
    fi
fi

echo "🚀 Starting Django development server..."
echo ""
echo "Your Django app will be available at:"
echo "👉 http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Django server
python manage.py runserver 8000