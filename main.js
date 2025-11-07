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
      try {
        execSync('pkill -9 -f "manage.py runserver" 2>/dev/null || true', { stdio: 'ignore' });
      } catch (e) {
        // Ignore if pkill fails
      }
      try {
        execSync(`fuser -k ${DJANGO_PORT}/tcp 2>/dev/null || true`, { stdio: 'ignore' });
      } catch (e) {
        // fuser might not be available, try lsof instead
        try {
          const { exec } = require('child_process');
          exec(`lsof -ti:${DJANGO_PORT} | xargs kill -9 2>/dev/null || true`, { stdio: 'ignore' });
        } catch (e2) {
          // Ignore all errors
        }
      }
    }
  } catch (e) {
    // Ignore all cleanup errors - they're not critical
  }
}

// Function to check if Django server is running
function checkDjangoServer(port = DJANGO_PORT) {
  return new Promise((resolve) => {
    console.log(`[DEBUG] checkDjangoServer() called for port ${port}`);
    const client = net.createConnection({ port }, () => {
      console.log(`[DEBUG] ✓ Connection successful to port ${port}`);
      client.end();
      resolve(true);
    });
    client.on('error', (err) => {
      console.log(`[DEBUG] ✗ Connection failed to port ${port}:`, err.code);
      resolve(false);
    });
  });
}

// Function to wait for Django server to start
async function waitForDjangoServer(port = DJANGO_PORT, maxAttempts = 30) {
  console.log(`[DEBUG] waitForDjangoServer() called for port ${port}, maxAttempts: ${maxAttempts}`);
  for (let i = 0; i < maxAttempts; i++) {
    console.log(`[DEBUG] Attempt ${i + 1}/${maxAttempts}...`);
    const isRunning = await checkDjangoServer(port);
    if (isRunning) {
      console.log('[DEBUG] ✓ Django server is ready!');
      return true;
    }
    console.log(`[DEBUG] Server not ready yet, waiting 1 second...`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  console.log(`[DEBUG] ✗ waitForDjangoServer() timed out after ${maxAttempts} attempts`);
  return false;
}

// Function to start Django server
function startDjangoServer() {
  return new Promise((resolve, reject) => {
    console.log('========================================');
    console.log('[DEBUG] startDjangoServer() called');
    console.log('[DEBUG] Project directory:', __dirname);
    console.log('[DEBUG] Platform:', process.platform);
    
    // Verify we're in the correct project directory
    const fs = require('fs');
    const manageFile = path.join(__dirname, 'manage.py');
    console.log('[DEBUG] Checking for manage.py at:', manageFile);
    
    if (!fs.existsSync(manageFile)) {
      console.error('[DEBUG] ERROR: manage.py not found!');
      console.error('[DEBUG] Directory listing:', fs.readdirSync(__dirname).join(', '));
      reject(new Error('Wrong project directory'));
      return;
    }
    
    console.log('[DEBUG] ✓ manage.py found');
    
    // Use the simple startup script
    const isWindows = process.platform === 'win32';
    const scriptPath = path.join(__dirname, 'start_django.sh');
    console.log('[DEBUG] Script path:', scriptPath);
    console.log('[DEBUG] Script exists?', fs.existsSync(scriptPath));
    console.log('[DEBUG] Is Windows?', isWindows);
    
    // Check if bash is available
    const { execSync } = require('child_process');
    try {
      const bashCheck = execSync('bash --version', { encoding: 'utf8', timeout: 2000 });
      console.log('[DEBUG] ✓ Bash found:', bashCheck.split('\n')[0]);
    } catch (e) {
      console.error('[DEBUG] ❌ Bash NOT found in PATH!');
      console.error('[DEBUG] Error:', e.message);
    }
    
    console.log('[DEBUG] Spawning Django process...');
    console.log('[DEBUG] Command: bash');
    console.log('[DEBUG] Args:', [scriptPath]);
    console.log('[DEBUG] CWD:', __dirname);
    
    try {
      if (isWindows) {
        djangoProcess = spawn('bash', [scriptPath], {
          cwd: __dirname,
          stdio: ['pipe', 'pipe', 'pipe'],
          env: { ...process.env, PYTHONUNBUFFERED: '1' },
          shell: false
        });
      } else {
        djangoProcess = spawn('bash', [scriptPath], {
          cwd: __dirname,
          stdio: ['pipe', 'pipe', 'pipe'],
          env: { ...process.env, PYTHONUNBUFFERED: '1' },
          shell: false
        });
      }
      console.log('[DEBUG] ✓ Process spawned, PID:', djangoProcess.pid);
    } catch (spawnError) {
      console.error('[DEBUG] ❌ SPAWN FAILED:', spawnError);
      reject(spawnError);
      return;
    }

    let resolved = false;
    let stdoutBuffer = '';
    let stderrBuffer = '';

    djangoProcess.stdout.on('data', (data) => {
      const output = data.toString();
      stdoutBuffer += output;
      console.log('[DEBUG] [Django stdout]:', output.trim());
      if (output.includes('Starting development server') && !resolved) {
        console.log('[DEBUG] ✓ Detected "Starting development server" message');
        resolved = true;
        setTimeout(() => {
          console.log('[DEBUG] Resolving promise after 2 second delay');
          resolve();
        }, 2000);
      }
    });

    djangoProcess.stderr.on('data', (data) => {
      const message = data.toString();
      stderrBuffer += message;
      console.error('[DEBUG] [Django stderr]:', message.trim());
    });

    djangoProcess.on('close', (code) => {
      console.log('[DEBUG] ========================================');
      console.log('[DEBUG] Django process CLOSED');
      console.log('[DEBUG] Exit code:', code);
      console.log('[DEBUG] Resolved?', resolved);
      console.log('[DEBUG] Last stdout:', stdoutBuffer.slice(-500));
      console.log('[DEBUG] Last stderr:', stderrBuffer.slice(-500));
      console.log('[DEBUG] ========================================');
    });

    djangoProcess.on('error', (error) => {
      console.error('[DEBUG] ========================================');
      console.error('[DEBUG] ❌ CRITICAL: Process error event fired!');
      console.error('[DEBUG] Error code:', error.code);
      console.error('[DEBUG] Error message:', error.message);
      console.error('[DEBUG] Error syscall:', error.syscall);
      console.error('[DEBUG] This usually means bash is not found in PATH');
      console.error('[DEBUG] ========================================');
      if (!resolved) {
        resolved = true;
        reject(error);
      }
    });

    // Fallback: resolve after 10 seconds
    setTimeout(() => {
      if (!resolved) {
        console.log('[DEBUG] ========================================');
        console.log('[DEBUG] ⚠️  TIMEOUT: 10 seconds elapsed');
        console.log('[DEBUG] Resolved?', resolved);
        console.log('[DEBUG] Process still running?', !djangoProcess.killed);
        console.log('[DEBUG] Checking if server is actually running...');
        checkDjangoServer(DJANGO_PORT).then((isRunning) => {
          console.log('[DEBUG] Server check result:', isRunning);
        });
        console.log('[DEBUG] ========================================');
        resolved = true;
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
      allowRunningInsecureContent: true,
      // Use a unique partition to isolate cookies/sessions from other Electron apps
      // This ensures each Electron/Django project maintains its own separate session
      partition: 'persist:kemcoengineeringapp'
    },
    title: 'Kemco Engineering App',
    show: true // Show immediately
  });

  // Load loading page first
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));

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

  // Handle page load failures with retry logic to prevent infinite loop
  let failLoadCount = 0;
  const maxFailLoadRetries = 3;
  let isRetrying = false;
  
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL, isMainFrame) => {
    if (!isMainFrame) return; // Only handle main frame failures
    
    failLoadCount++;
    console.log(`Page load failed: ${errorCode} - ${errorDescription} (attempt ${failLoadCount})`);
    
    if (failLoadCount < maxFailLoadRetries && !isRetrying) {
      isRetrying = true;
      // Retry loading after a short delay
      setTimeout(async () => {
        console.log(`Retrying load... (${failLoadCount}/${maxFailLoadRetries})`);
        const isRunning = await checkDjangoServer(DJANGO_PORT);
        if (isRunning) {
          mainWindow.loadURL(`http://127.0.0.1:${DJANGO_PORT}`);
        } else {
          console.log('Django server not running, showing loading page...');
          mainWindow.loadFile(path.join(__dirname, 'loading.html'));
        }
        isRetrying = false;
      }, 2000);
    } else if (failLoadCount >= maxFailLoadRetries) {
      // Too many failures, show loading page and reset
      console.log('Too many load failures, showing loading page...');
      mainWindow.loadFile(path.join(__dirname, 'loading.html'));
      failLoadCount = 0; // Reset counter
      isRetrying = false;
    }
  });
  
  // Reset fail count on successful load
  mainWindow.webContents.on('did-finish-load', () => {
    failLoadCount = 0;
    isRetrying = false;
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
      // Note: explorer.exe often returns non-zero exit code even when it successfully opens
      const { exec } = require('child_process');
      const normalizedPath = filePath.replace(/\//g, '\\');

      return new Promise((resolve) => {
        // Use exec with shell to properly handle paths with spaces and special characters
        // explorer.exe often returns non-zero exit code even when it successfully opens
        const command = `explorer /select,"${normalizedPath}"`;

        exec(command, {
          shell: true,
          windowsHide: true
        }, (error, stdout, stderr) => {
          // Always return success - explorer usually opens even if there's an error code
          // This is a known Windows quirk where explorer returns non-zero even on success
          resolve({ success: true });
        });
      });
    } else if (process.platform === 'darwin') {
      // macOS: Reveal in Finder
      await shell.openPath(path.dirname(filePath));
      return { success: true };
    } else {
      // Linux: Open file manager (xdg-open works on most Linux distributions including ZorinOS)
      const { exec } = require('child_process');
      const directory = path.dirname(filePath);
      
      return new Promise((resolve) => {
        // Try xdg-open first (standard on most Linux distros)
        exec(`xdg-open "${directory}"`, (error, stdout, stderr) => {
          if (error) {
            // Fallback to shell.openPath if xdg-open fails
            shell.openPath(directory).then(() => {
              resolve({ success: true });
            }).catch(() => {
              resolve({ success: true }); // Return success anyway
            });
          } else {
            resolve({ success: true });
          }
        });
      });
    }
  } catch (error) {
    console.error('Error opening location:', error);
    // Even on error, file manager usually opens, so return success
    return { success: true };
  }
});

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  console.log('Another instance is already running. Exiting...');
  app.quit();
} else {
  app.on('second-instance', () => {
    // Someone tried to run a second instance, focus our window instead
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// Handle app ready
app.whenReady().then(async () => {
  console.log('Electron app is ready');
  
  // Create window immediately - don't wait for Django
  // Window will show loading.html first, then switch to Django when ready
  createWindow();
  
  try {
    console.log('[DEBUG] ========================================');
    console.log('[DEBUG] Checking if Django is already running...');
    const isAlreadyRunning = await checkDjangoServer(DJANGO_PORT);
    console.log('[DEBUG] Django already running?', isAlreadyRunning);
    
    if (!isAlreadyRunning) {
      console.log('[DEBUG] Django server not running, starting it...');
      try {
        await startDjangoServer();
        console.log('[DEBUG] startDjangoServer() promise resolved');
      } catch (startError) {
        console.error('[DEBUG] ❌ startDjangoServer() REJECTED:', startError);
        console.error('[DEBUG] Error details:', startError.message);
      }
      
      // Wait for server to be ready (non-blocking)
      console.log('[DEBUG] Starting waitForDjangoServer()...');
      waitForDjangoServer(DJANGO_PORT, 20).then((serverReady) => {
        console.log('[DEBUG] waitForDjangoServer() completed, serverReady:', serverReady);
        if (serverReady) {
          console.log('[DEBUG] ✓ Django server is now ready! Loading URL...');
          // Reload the window to show Django content
          if (mainWindow && !mainWindow.isDestroyed()) {
            const url = `http://127.0.0.1:${DJANGO_PORT}`;
            console.log('[DEBUG] Loading URL:', url);
            mainWindow.loadURL(url).then(() => {
              console.log('[DEBUG] ✓ URL loaded successfully');
            }).catch((loadError) => {
              console.error('[DEBUG] ❌ Failed to load URL:', loadError);
            });
          } else {
            console.error('[DEBUG] ❌ Main window is null or destroyed!');
          }
        } else {
          console.warn('[DEBUG] ⚠️  Django server not ready after waiting');
          console.log('[DEBUG] You can try starting Django manually with: ./run_django.sh');
        }
      }).catch((err) => {
        console.error('[DEBUG] ❌ Error in waitForDjangoServer():', err);
      });
    } else {
      console.log('[DEBUG] ✓ Django server is already running');
      if (mainWindow && !mainWindow.isDestroyed()) {
        const url = `http://127.0.0.1:${DJANGO_PORT}`;
        console.log('[DEBUG] Loading URL immediately:', url);
        mainWindow.loadURL(url);
      }
    }
    console.log('[DEBUG] ========================================');
    
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