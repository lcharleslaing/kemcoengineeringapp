# 🚀 Complete Electron-Django Installer Build Prompt

Copy this entire prompt and paste it into a new chat to get step-by-step help building distributable installers for your app.

---

## Project Context

I have a working **Django + Electron desktop application** called **LeeCharlesLaing.net** that currently runs perfectly with `npm start`. I want to create **installable packages** (Windows `.exe`, macOS `.dmg`, Linux `.AppImage`/`.deb`) that bundle everything together so users can install and run it without manually setting up Python, Django, or Conda.

### Current Project Structure

```
leecharleslaingdotnet/
├── main.js                 # Electron main process
├── loading.html            # Splash screen
├── package.json            # Node/Electron config
├── manage.py               # Django entry point
├── db.sqlite3              # SQLite database
├── myproject/              # Django project settings
├── core/                   # Main Django app
├── my_calendar/            # Calendar app
├── my_budget/              # Budget app
├── my_meds/                # Medication tracker app
├── site_settings/          # Settings app
├── templates/              # Shared templates
├── media/                  # User uploads
├── environment.yml         # Conda environment spec
├── requirements.txt        # Python dependencies
├── start_django.sh         # Django startup script
├── cleanup_port.sh         # Port cleanup script
└── node_modules/           # Node dependencies
```

### Current Technology Stack

**Frontend:**
- Electron 33.2.1
- electron-builder (for packaging)
- Node.js (via system or nvm)

**Backend:**
- Django 5.1.4
- Python 3.12 (in Conda environment named "django")
- SQLite database
- Key Django apps: core, my_calendar, my_budget, my_meds, site_settings

**Key Python Packages:**
- django, pillow, python-dateutil, ofxparse, weasyprint (see requirements.txt)

**Environment Management:**
- Conda environment: `django`
- Activated via: `conda activate django`

### How It Currently Works (npm start)

1. **Cleanup Phase** (`prestart` script):
   - Runs `cleanup_port.sh` to kill any existing Django processes on port 8000
   - Uses `pkill`, `lsof`, and `fuser` for robust cleanup

2. **Startup Phase**:
   - Electron launches and shows splash screen (`loading.html`)
   - `main.js` executes `start_django.sh` which:
     - Activates Conda environment
     - Runs `python manage.py runserver 127.0.0.1:8000`
   - Electron waits for Django to respond on port 8000
   - Once ready, loads `http://127.0.0.1:8000` in the main window

3. **Shutdown Phase**:
   - On app quit, `main.js` sends `SIGKILL` to Django process
   - Runs cleanup commands to ensure port 8000 is freed
   - `poststart` also runs cleanup

### Critical Features to Preserve

✅ **Auto-cleanup of port 8000** before and after running
✅ **Splash screen** while Django starts up
✅ **Single-instance** enforcement (only one app at a time)
✅ **Graceful shutdown** that kills Django and frees the port
✅ **User data persistence** (db.sqlite3, media uploads)
✅ **All Django apps functional**: Calendar, Budget, Meds, Settings

---

## 🎯 Goal: Create Distributable Installers

I want to create installers that:

### Windows (`.exe` installer or portable)
- Bundle Python runtime + Django + all dependencies
- Install to Program Files or run portably
- Create desktop shortcut and Start Menu entry
- Include uninstaller
- Auto-start Django backend when app launches
- Clean shutdown and cleanup

### macOS (`.dmg` or `.app`)
- Bundle Python runtime + Django + all dependencies
- Drag-to-Applications installer
- Code-signed (if possible, guide me through)
- Native macOS app behavior
- Dock icon with proper branding

### Linux (`.AppImage` and/or `.deb`/`.rpm`)
- Bundle Python runtime + Django + all dependencies
- Self-contained, no external dependencies
- Desktop integration (`.desktop` file, icons)
- Works on Ubuntu, Fedora, Arch, etc.

### User Experience Requirements
1. **One-click install**: Double-click installer → installed and ready
2. **No manual setup**: User never sees terminal, Conda, pip, or Django
3. **Clean uninstall**: Remove all files, no leftovers
4. **Auto-updates** (optional but nice): Check for updates on launch
5. **Data persistence**: User data (database, uploads) survives updates
6. **Cross-platform consistency**: Same UX on all platforms

---

## 🔧 Technical Requirements

### 1. Bundle Python with Electron

**Challenge**: Electron apps are JavaScript; we need to bundle a Python runtime.

**Solutions to explore:**
- **PyInstaller**: Package Django app as standalone executable
- **Briefcase**: Cross-platform Python app bundler
- **pyoxidizer**: Rust-based Python bundler
- **conda-constructor**: Create minimal Conda distribution
- **python-build-standalone**: Pre-built Python binaries

**Recommendation**: Use **PyInstaller** to create a `django-server` executable that Electron can spawn, OR bundle a minimal Python runtime and run `manage.py` directly.

### 2. electron-builder Configuration

`electron-builder` handles Electron app packaging. I need you to:
- Configure `package.json` → `build` section
- Set app name, ID, icons, directories
- Configure target formats per platform
- Handle extra resources (Django files, Python runtime)
- Sign and notarize (guide me through certificates)

### 3. File Structure for Packaging

```
build/
├── icon.icns           # macOS icon (512x512+)
├── icon.ico            # Windows icon
├── icon.png            # Linux icon (512x512+ PNG)
└── ...

resources/              # Files to bundle with app
├── django-server/      # Bundled Django app or Python runtime
│   ├── manage.py
│   ├── myproject/
│   ├── core/
│   └── ...
└── ...

dist/                   # Output directory (after build)
├── win/                # Windows installer
├── mac/                # macOS DMG
└── linux/              # Linux AppImage/deb
```

### 4. Platform-Specific Adjustments

**Windows:**
- Bundle Python 3.12 embeddable distribution OR PyInstaller exe
- Use `taskkill` instead of `pkill` for cleanup
- Handle Windows Defender / SmartScreen warnings

**macOS:**
- Bundle Python framework or PyInstaller bundle
- Code signing with Apple Developer account (guide me)
- Notarization for Gatekeeper (guide me)
- Use Activity Monitor for process management

**Linux:**
- Bundle Python or use PyInstaller
- No code signing needed
- `.desktop` file for launcher integration
- Icon installation in `~/.local/share/icons`

### 5. Data Persistence Strategy

**User data location** (database, uploads):
- Windows: `%APPDATA%\LeeCharlesLaing.net\`
- macOS: `~/Library/Application Support/LeeCharlesLaing.net/`
- Linux: `~/.config/LeeCharlesLaing.net/` or `~/.local/share/LeeCharlesLaing.net/`

**On first run:**
- Copy blank `db.sqlite3` to user data dir
- Run Django migrations
- Create default superuser (or prompt for setup)

**On updates:**
- Preserve existing database and media files
- Run migrations if needed

### 6. Django Configuration Changes

**Settings adjustments for production:**
- `DEBUG = False` in packaged version
- `ALLOWED_HOSTS = ['127.0.0.1', 'localhost']`
- `SECRET_KEY` from environment or generated on first run
- `DATABASES` path to user data directory
- `MEDIA_ROOT` and `MEDIA_URL` to user data directory
- `STATIC_ROOT` collected in bundle

**Run on first launch:**
```bash
python manage.py collectstatic --noinput
python manage.py migrate
```

---

## 📋 Step-by-Step Implementation Plan

### Phase 1: Prepare Django for Bundling
1. Create production settings file (`myproject/settings_prod.py`)
2. Set up static file collection
3. Create initialization script for first run
4. Test Django runs standalone (without Conda)

### Phase 2: Bundle Python + Django
5. Choose bundling method (PyInstaller recommended)
6. Create spec file for PyInstaller
7. Test bundled Django executable runs independently
8. Ensure all dependencies are included

### Phase 3: Update Electron for Bundled Django
9. Modify `main.js` to detect bundled vs development mode
10. Update Django spawn logic to use bundled executable
11. Handle paths for bundled resources
12. Test in development mode still works

### Phase 4: Configure electron-builder
13. Create icons (512x512+ for all platforms)
14. Configure `package.json` → `build` section
15. Set up file associations and metadata
16. Configure `extraResources` for Django bundle
17. Test local build: `npm run build`

### Phase 5: Platform-Specific Builds
18. **Windows**: Build and test `.exe` installer
19. **macOS**: Build `.dmg`, handle signing/notarization
20. **Linux**: Build `.AppImage` and/or `.deb`
21. Test each installer on clean VM or system

### Phase 6: Polish and Distribution
22. Implement auto-update mechanism (optional)
23. Create release workflow (GitHub Actions?)
24. Write user documentation
25. Publish installers (GitHub Releases, website, etc.)

---

## 🛠️ Specific Configuration Files to Create/Modify

### 1. `myproject/settings_prod.py`
Production Django settings with:
- `DEBUG = False`
- Dynamic `SECRET_KEY`
- User data directory paths
- Static files configuration

### 2. `package.json` → `build` section
electron-builder configuration:
- App ID, name, copyright
- Directories for output and resources
- Platform-specific targets
- File associations
- extraResources glob patterns
- Signing configuration

### 3. `build-django.py` or `django.spec` (PyInstaller)
Script to bundle Django app into standalone executable.

### 4. `main.js` updates
- Detect if running from bundle or development
- Adjust paths to bundled Django executable
- Handle user data directory initialization
- Spawn bundled Django process

### 5. `first-run.js` or equivalent
Script to run on first launch:
- Create user data directories
- Copy blank database
- Run migrations
- Optionally create admin user

### 6. Icon files
- `build/icon.icns` (macOS, 512x512+ ICNS)
- `build/icon.ico` (Windows, multiple sizes)
- `build/icon.png` (Linux, 512x512+ PNG)

---

## ✅ Success Criteria

When you're done, I should be able to:

1. **Build installers** with one command:
   ```bash
   npm run build           # Build for current platform
   npm run build:win       # Windows
   npm run build:mac       # macOS
   npm run build:linux     # Linux
   ```

2. **Distribute** a single file (installer) per platform that users can download and run.

3. **Install** the app:
   - Windows: Run `.exe`, click through installer, launch from Start Menu
   - macOS: Open `.dmg`, drag to Applications, launch from Launchpad
   - Linux: Run `.AppImage` directly, or install `.deb` with `dpkg`

4. **Use** the app without any knowledge of Django, Python, or terminal commands.

5. **Uninstall** cleanly via OS-standard methods.

6. **Update** the app in the future by installing a new version (data persists).

---

## 🚨 Important Notes

- **Don't break development mode**: `npm start` should still work for development
- **Test on clean systems**: VMs or fresh installs to ensure no hidden dependencies
- **File size**: Final installers may be 100-300 MB (Python + Django + dependencies)
- **Security**: No sensitive data in the bundle (generate SECRET_KEY at runtime)
- **Licenses**: Ensure all bundled components are properly licensed
- **Code signing**: Windows and macOS may require code signing certificates (guide me on getting these if needed)

---

## 📚 Additional Context

### Current package.json scripts:
```json
{
  "scripts": {
    "start": "electron .",
    "prestart": "./cleanup_port.sh",
    "poststart": "./cleanup_port.sh",
    "django": "./start_django.sh",
    "cleanup": "./cleanup_port.sh"
  }
}
```

### Current main.js key sections:
- `startDjangoServer()`: Spawns `start_django.sh`
- `waitForDjango()`: Polls port 8000 until Django responds
- `createMainWindow()`: Creates Electron browser window
- Cleanup handlers on `window-all-closed`, `before-quit`, `SIGTERM`, `SIGINT`

### Django apps structure:
- All apps follow standard Django patterns
- Use SQLite (not PostgreSQL or MySQL)
- Media files stored locally
- No external APIs or services (fully offline-capable)

---

## 🎬 Start Here

Begin by analyzing my current project structure and:

1. **Confirm the approach**: Should we use PyInstaller, Briefcase, or another method?
2. **Outline the steps**: Give me a clear, numbered checklist
3. **Create necessary files**: Settings, configs, scripts
4. **Test incrementally**: Build → test → fix → repeat
5. **Document everything**: So I can rebuild or troubleshoot later

**Let's build professional, distributable installers for LeeCharlesLaing.net!** 🚀

---

## Optional Enhancements (After Basic Build Works)

- Auto-update functionality (electron-updater)
- Crash reporting (Sentry)
- Analytics (optional, privacy-friendly)
- Custom installer UI/branding
- Command-line arguments support
- System tray icon with quick actions
- Multi-user support (separate databases per OS user)
- Backup/restore functionality
- Export app data to ZIP

---

**Please start by assessing the best bundling approach for my project and provide a detailed implementation plan!**

