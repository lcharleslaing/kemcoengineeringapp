# Django Electron Desktop App

A desktop application that wraps a Django web application using Electron, providing a native desktop experience for your Django app.

## 🚀 Features

- **Django Backend**: Full Django web application with SQLite database
- **Electron Frontend**: Native desktop wrapper with system integration
- **Auto-startup**: Automatically starts Django server when the app launches
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Self-contained**: Includes all dependencies in the built application

## �️ Installation & Setup

### Prerequisites
- **Conda** or **Miniconda**
- **Git**

### Option 1: Using Conda Environment (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd django-electron-base

# Create and activate environment
conda env create -f environment.yml
conda activate django-electron

# Install Node.js dependencies
npm install

# Run Django migrations
python manage.py migrate

# Start the app
npm start
```

### Option 2: Using Separate Environments

```bash
# Clone the repository
git clone <your-repo-url>
cd django-electron-base

# Set up Django environment
conda create -n django python=3.12 django
conda activate django
pip install -r requirements.txt

# Set up Node.js environment  
conda activate base  # or create separate env with nodejs
npm install

# Run Django migrations
conda activate django
python manage.py migrate

# Start the app
conda activate base
npm start
```

## 🎯 Running the Application

### **Simple Commands**

#### **Start Desktop App**
```bash
npm start
```
This starts your Django Electron desktop application.

#### **Start Django Only** 
```bash
npm run django
```
This starts just the Django server at http://127.0.0.1:8000

#### **Alternative (Same as npm start)**
```bash
./run.sh
```

### **That's it!** 🎉

The app will:
1. Automatically start Django server
2. Open Electron desktop window
3. Load your Django app inside the window

## 📁 Project Structure

```
django-electron-base/
├── main.js                 # Electron main process
├── loading.html            # Loading screen
├── package.json            # Node.js configuration  
├── run.sh                  # 🚀 Simple launcher
├── run_django.sh          # 🐍 Django only launcher
├── start_django.sh        # Django startup helper
├── myproject/             # Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                  # Django app
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── migrations/
├── manage.py              # Django management script
└── db.sqlite3            # SQLite database
```

## 🔧 Configuration

### Django Settings

The Django application is configured in `myproject/settings.py`. Key settings:

- **Debug Mode**: Enabled for development
- **Database**: SQLite (`db.sqlite3`)
- **Installed Apps**: Includes the `core` app
- **Static Files**: Configured for development

### Electron Settings

Electron configuration in `main.js`:

- **Window Size**: 1200x800 pixels
- **Security**: Context isolation enabled
- **Auto-start**: Django server starts automatically
- **Port**: Django runs on port 8000

## 🏗️ Building for Distribution

### Install Build Tools

```bash
npm install electron-builder --save-dev
```

### Build Commands

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build-win    # Windows
npm run build-mac    # macOS
npm run build-linux  # Linux
```

Built applications will be in the `dist/` directory.

## 🧪 Testing

Run the setup verification script:

```bash
./test_setup.sh
```

This checks:
- ✅ Conda environment
- ✅ Django installation
- ✅ Node.js and Electron
- ✅ Project structure
- ✅ Django configuration

## 🐛 Troubleshooting

### Electron Won't Start

1. **Sandbox Issues**: The app uses `--no-sandbox` flag for compatibility
2. **Display Issues**: Electron requires a GUI environment
3. **Port Conflicts**: Django runs on port 8000 by default

### Django Issues

1. **Database**: Run `python manage.py migrate` if needed
2. **Static Files**: Run `python manage.py collectstatic` for production
3. **Environment**: Ensure `conda activate django` is working

### Common Solutions

```bash
# Kill any existing Django processes
pkill -f "python manage.py runserver"

# Reinstall Node dependencies
rm -rf node_modules package-lock.json
npm install

# Reset Django database
rm db.sqlite3
python manage.py migrate
```

## 📝 Development Tips

1. **Django Development**: Use the standard Django development workflow
2. **Electron Development**: Modify `main.js` for desktop-specific features
3. **Hot Reload**: Django auto-reloads, restart Electron for main process changes
4. **Debugging**: Use `npm run dev` to enable developer tools

## 🚀 Next Steps

1. **Add your Django views and templates** in the `core` app
2. **Customize the Electron window** in `main.js`
3. **Add desktop features** like system tray, notifications
4. **Build for distribution** using the build commands

## 📜 License

MIT License - feel free to use this as a template for your own Django desktop applications!

---

**Your Django web app is now a desktop application!** 🎉