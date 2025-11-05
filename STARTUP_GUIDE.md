# 🚀 LeeCharlesLaing.net Startup Guide

## Quick Start

Just run:
```bash
npm start
```

That's it! The app will automatically:
1. ✅ Clean up any Django processes on port 8000
2. ✅ Verify it's in the correct project directory
3. ✅ Start Django from this project only
4. ✅ Open Electron with the app
5. ✅ Clean up when you exit

## What Happens Automatically

### On Startup (`npm start`):
- **Pre-start**: Runs `cleanup_port.sh` to kill any processes on port 8000
- **Start**: Launches Electron
- **Django Start**: `start_django.sh` runs with triple-redundant cleanup:
  1. Kills all Django processes by name
  2. Kills any process using port 8000
  3. Uses `fuser` to force-kill port 8000
- **Verification**: Confirms port is free before starting Django

### On Exit (Ctrl+C or close window):
- **Electron cleanup**: Force-kills Django process
- **Port cleanup**: Runs cleanup commands again
- **Post-start**: Runs `cleanup_port.sh` one final time

## Manual Commands

### Clean up port 8000 manually:
```bash
npm run cleanup
```
or
```bash
./cleanup_port.sh
```

### Start Django only (without Electron):
```bash
npm run django
```

### Check what's on port 8000:
```bash
lsof -i :8000
```

### Kill all Django servers manually:
```bash
pkill -9 -f "manage.py runserver"
```

## Multiple Django Projects?

If you have multiple Django projects, each should use a different port:

**Project 1 (leecharleslaingdotnet)**: Port 8000 ← This project  
**Project 2**: Port 8001  
**Project 3**: Port 8002  

To change this project's port, edit:
1. `start_django.sh` - change `8000` to your port
2. `cleanup_port.sh` - change `8000` to your port
3. `main.js` - change all `8000` references to your port

## Troubleshooting

### "Port 8000 is still in use!"
Run manual cleanup:
```bash
./cleanup_port.sh
```

If that doesn't work:
```bash
# Find what's using the port
lsof -i :8000

# Kill it manually (replace PID with the actual process ID)
kill -9 PID
```

### Wrong project opens
This shouldn't happen anymore! The scripts now:
- Verify the project directory contains `manage.py`
- Kill ALL processes on port 8000 before starting
- Start Django from the script's directory only

### App won't start
1. Make sure scripts are executable:
```bash
chmod +x start_django.sh cleanup_port.sh
```

2. Check conda environment:
```bash
conda activate django
python manage.py check
```

3. Try starting Django manually first:
```bash
./start_django.sh
```

4. Then in another terminal:
```bash
npm start
```

## Clean State Reset

If things get really messy:
```bash
# Kill everything
pkill -9 -f "manage.py runserver"
pkill -9 -f electron

# Clean up port
./cleanup_port.sh

# Fresh start
npm start
```

## Exit Methods

All of these will clean up properly:
- ✅ Close the Electron window
- ✅ Press Ctrl+C in the terminal
- ✅ Kill the npm process
- ✅ System shutdown

The cleanup happens automatically in all cases!

