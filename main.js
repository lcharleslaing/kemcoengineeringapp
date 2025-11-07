const { app, BrowserWindow, shell, globalShortcut, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const net = require('net');

// Enhanced Electron configuration for Wayland compatibility
app.commandLine.appendSwitch('--no-sandbox');
app.commandLine.appendSwitch('--disable-setuid-sandbox');
app.commandLine.appendSwitch('--disable-gpu-sandbox');
app.commandLine.appendSwitch('--disable-dev-shm-usage');
app.commandLine.appendSwitch('--disable-extensions');
app.commandLine.appendSwitch('--disable-background-timer-throttling');
app.commandLine.appendSwitch('--disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('--disable-renderer-backgrounding');
app.commandLine.appendSwitch('--disable-features=TranslateUI');

// Wayland-specific configuration
if (process.platform === 'linux') {
  // Set environment variables for Wayland
  process.env.ELECTRON_OZONE_PLATFORM_HINT = 'auto';
  
  // Try Wayland first, then fallback to X11
  if (process.env.WAYLAND_DISPLAY && !process.env.FORCE_X11) {
    console.log('Detected Wayland, configuring for Wayland support...');
    app.commandLine.appendSwitch('--enable-features=UseOzonePlatform,WaylandWindowDecorations');
    app.commandLine.appendSwitch('--ozone-platform=wayland');
    app.commandLine.appendSwitch('--enable-wayland-ime');
  } else {
    console.log('Using X11 compatibility mode...');
    app.commandLine.appendSwitch('--enable-features=UseOzonePlatform');
    app.commandLine.appendSwitch('--ozone-platform=x11');
  }
  
  // Additional Linux compatibility flags
  app.commandLine.appendSwitch('--disable-gpu-compositing');
  app.commandLine.appendSwitch('--disable-software-rasterizer');
}

// Django server port - change this if you need a different port
const DJANGO_PORT = 8001;

let djangoProcess = null;
let mainWindow = null;

// Cross-platform cleanup function
function cleanupDjangoPort() {
  const { execSync } = require('child_process');
  const isWindows = process.platform === 'win32';
  
  try {
    if (isWindows) {
      // Windows: Use PowerShell or bash (if Git Bash is available)
      // Try to kill processes using the Django port
      try {
        execSync(`netstat -ano | findstr :${DJANGO_PORT}`, { stdio: 'ignore' });
        // If we found something, try to kill it (would need to parse PID)
        // For now, just try taskkill on common Python processes
        execSync('taskkill /F /IM python.exe /FI "WINDOWTITLE eq *manage.py*" 2>nul || true', { stdio: 'ignore', shell: true });
      } catch (e) {
        // Ignore errors
      }
      // Also try bash cleanup script if available
      try {
        execSync('bash cleanup_port.sh 2>/dev/null || true', { stdio: 'ignore', shell: false });
      } catch (e) {
        // Ignore if bash not available
      }
    } else {
      // Linux/Mac: Use standard Unix commands
      execSync('pkill -9 -f "manage.py runserver" 2>/dev/null || true', { stdio: 'ignore' });
      execSync(`fuser -k ${DJANGO_PORT}/tcp 2>/dev/null || true`, { stdio: 'ignore' });
    }
  } catch (e) {
    // Ignore all cleanup errors - they're not critical
  }
}

// Function to check if Django server is running
function checkDjangoServer(port = DJANGO_PORT) {
  return new Promise((resolve) => {
    const client = net.createConnection({ port }, () => {
      client.end();
      resolve(true);
    });
    client.on('error', () => {
      resolve(false);
    });
  });
}

// Function to wait for Django server to start
async function waitForDjangoServer(port = DJANGO_PORT, maxAttempts = 30) {
  console.log('Waiting for Django server to start...');
  for (let i = 0; i < maxAttempts; i++) {
    const isRunning = await checkDjangoServer(port);
    if (isRunning) {
      console.log('Django server is ready!');
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log(`Attempt ${i + 1}/${maxAttempts}...`);
  }
  return false;
}

// Function to start Django server
function startDjangoServer() {
  return new Promise((resolve, reject) => {
    console.log('Starting Django server...');
    console.log('Project directory:', __dirname);
    
    // Verify we're in the leecharleslaingdotnet project
    const fs = require('fs');
    const manageFile = path.join(__dirname, 'manage.py');
    if (!fs.existsSync(manageFile)) {
      console.error('ERROR: manage.py not found. Wrong project directory?');
      console.error('Expected directory:', __dirname);
      reject(new Error('Wrong project directory'));
      return;
    }
    
    console.log('✓ Verified correct project directory');
    
    // Use the simple startup script
    // On Windows, we need to use 'bash' to execute .sh files
    // On Linux, we can execute directly or use bash
    const isWindows = process.platform === 'win32';
    const scriptPath = path.join(__dirname, 'start_django.sh');
    
    if (isWindows) {
      // On Windows, use bash to execute the script
      djangoProcess = spawn('bash', [scriptPath], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
        shell: false
      });
    } else {
      // On Linux/Mac, can execute directly or use bash
      djangoProcess = spawn('bash', [scriptPath], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
        shell: false
      });
    }

    let resolved = false;

    djangoProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`Django: ${output.trim()}`);
      if (output.includes('Starting development server') && !resolved) {
        resolved = true;
        setTimeout(resolve, 2000); // Give Django 2 more seconds to fully start
      }
    });

    djangoProcess.stderr.on('data', (data) => {
      const message = data.toString();
      console.error(`Django Error: ${message.trim()}`);
    });

    djangoProcess.on('close', (code) => {
      console.log(`Django process exited with code ${code}`);
    });

    djangoProcess.on('error', (error) => {
      console.error('Failed to start Django process:', error);
      if (!resolved) {
        resolved = true;
        reject(error);
      }
    });

    // Fallback: resolve after 10 seconds
    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        console.log('Django startup timeout reached, checking if server is responsive...');
        resolve();
      }
    }, 10000);
  });
}

// Function to create the main window
function createWindow() {
  console.log('Creating Electron window...');
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,  // Enable for file path access in desktop app
      contextIsolation: false, // Disable to allow direct Node.js access
      enableRemoteModule: false,
      webSecurity: false, // Disabled for local development
      allowRunningInsecureContent: true
    },
    title: 'LeeCharlesLaing.net',
    show: true // Show immediately
  });

  // Load the Django app
  console.log(`Loading Django app at http://127.0.0.1:${DJANGO_PORT}`);
  mainWindow.loadURL(`http://127.0.0.1:${DJANGO_PORT}`);

  // Show window when ready (backup in case it was hidden)
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready, ensuring it is visible...');
    if (!mainWindow.isVisible()) {
      mainWindow.show();
    }
  });
  
  // Fallback: Show window after 2 seconds even if ready-to-show doesn't fire
  setTimeout(() => {
    if (mainWindow && !mainWindow.isDestroyed() && !mainWindow.isVisible()) {
      console.log('Showing window after timeout...');
      mainWindow.show();
    }
  }, 2000);

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle page load failures
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.log(`Page load failed: ${errorCode} - ${errorDescription}`);
    console.log('Loading fallback page...');
    mainWindow.loadFile(path.join(__dirname, 'loading.html'));
  });

  // Log navigation events
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Page loaded successfully');
  });
}

// Register IPC handlers for file operations (register once at app startup)
ipcMain.handle('open-file', async (event, filePath) => {
  try {
    await shell.openPath(filePath);
    return { success: true };
  } catch (error) {
    console.error('Error opening file:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('open-location', async (event, filePath) => {
  try {
    if (process.platform === 'win32') {
      // Windows: Open Explorer with file selected
      const { exec } = require('child_process');
      return new Promise((resolve) => {
        exec(`explorer /select,"${filePath.replace(/\//g, '\\')}"`, (error) => {
          if (error) {
            console.error('Error opening location:', error);
            resolve({ success: false, error: error.message });
          } else {
            resolve({ success: true });
          }
        });
      });
    } else if (process.platform === 'darwin') {
      // macOS: Reveal in Finder
      await shell.openPath(path.dirname(filePath));
      return { success: true };
    } else {
      // Linux: Open file manager
      await shell.openPath(path.dirname(filePath));
      return { success: true };
    }
  } catch (error) {
    console.error('Error opening location:', error);
    return { success: false, error: error.message };
  }
});

// Handle app ready
app.whenReady().then(async () => {
  console.log('Electron app is ready');
  
  // Create window immediately - don't wait for Django
  createWindow();
  
  try {
    // Check if Django is already running
    const isAlreadyRunning = await checkDjangoServer(DJANGO_PORT);
    
    if (!isAlreadyRunning) {
      console.log('Django server not running, starting it...');
      await startDjangoServer();
      
      // Wait for server to be ready (non-blocking)
      waitForDjangoServer(DJANGO_PORT, 20).then((serverReady) => {
        if (serverReady) {
          console.log('Django server is now ready!');
          // Reload the window to show Django content
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.loadURL(`http://127.0.0.1:${DJANGO_PORT}`);
          }
        } else {
          console.warn('Django server not ready yet, but window is open');
          console.log('You can try starting Django manually with: ./run_django.sh');
        }
      }).catch((err) => {
        console.error('Error waiting for Django:', err);
      });
    } else {
      console.log('Django server is already running');
    }
    
    // Register global keyboard shortcuts for history navigation
    globalShortcut.register('Alt+Left', () => {
      if (mainWindow && mainWindow.webContents.canGoBack()) {
        mainWindow.webContents.goBack();
      }
    });

    globalShortcut.register('Alt+Right', () => {
      if (mainWindow && mainWindow.webContents.canGoForward()) {
        mainWindow.webContents.goForward();
      }
    });
    
  } catch (error) {
    console.error('Error during startup:', error);
    console.log('Window created, but Django may not be ready');
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  
  // Unregister all global shortcuts
  globalShortcut.unregisterAll();
  
  // Kill Django process when app closes
  if (djangoProcess) {
    console.log('Stopping Django server...');
    try {
      djangoProcess.kill('SIGKILL'); // Force kill
    } catch (e) {
      console.error('Error killing Django process:', e);
    }
  }
  
  // Extra cleanup: kill any remaining Django processes
  console.log(`Cleaning up port ${DJANGO_PORT}...`);
  cleanupDjangoPort();
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Kill Django process when app quits
  if (djangoProcess) {
    console.log('Stopping Django server before quit...');
    try {
      djangoProcess.kill('SIGKILL'); // Force kill
    } catch (e) {
      console.error('Error killing Django process:', e);
    }
  }
  
  // Extra cleanup: kill any remaining Django processes
  console.log(`Final cleanup of port ${DJANGO_PORT}...`);
  cleanupDjangoPort();
});

// Handle app termination
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, cleaning up...');
  if (djangoProcess) {
    try {
      djangoProcess.kill('SIGKILL');
    } catch (e) {
      console.error('Error killing Django process:', e);
    }
  }
  
  // Force cleanup
  cleanupDjangoPort();
  
  app.quit();
});

process.on('SIGINT', () => {
  console.log('Received SIGINT, cleaning up...');
  if (djangoProcess) {
    try {
      djangoProcess.kill('SIGKILL');
    } catch (e) {
      console.error('Error killing Django process:', e);
    }
  }
  
  // Force cleanup
  cleanupDjangoPort();
  
  app.quit();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});