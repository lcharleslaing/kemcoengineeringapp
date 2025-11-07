# Session Isolation Fix Prompt

Copy and paste this entire prompt into your other Electron/Django project:

---

I'm working on multiple Electron/Django projects and each time I run either one, I have to login again because sessions are being shared between projects. The sessions are interfering with each other, causing me to lose my login state when switching between projects.

Please fix this so each project remembers my session separately. Here's what needs to be done:

## 1. Django Settings - Add Unique Session Cookie Names

In `myproject/settings.py` (or your Django settings file), add unique session and CSRF cookie names. Find the section with LOGIN settings and add these settings right after it:

```python
# Session settings - unique to this project to avoid conflicts with other Electron/Django apps
# This ensures each Electron app maintains its own separate session
SESSION_COOKIE_NAME = 'PROJECTNAME_sessionid'  # Replace PROJECTNAME with your project's folder name
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF cookie settings - also unique to this project
CSRF_COOKIE_NAME = 'PROJECTNAME_csrftoken'  # Replace PROJECTNAME with your project's folder name
```

**Important**: Replace `PROJECTNAME` with your actual project folder name (e.g., if your project folder is `myapp`, use `'myapp_sessionid'` and `'myapp_csrftoken'`). Make sure both cookie names use the same project identifier.

## 2. Electron Configuration - Add Unique Partition

In `main.js`, find the `createWindow()` function. In the `BrowserWindow` constructor, locate the `webPreferences` object and add a `partition` property:

```javascript
webPreferences: {
  nodeIntegration: true,
  contextIsolation: false,
  enableRemoteModule: false,
  webSecurity: false,
  allowRunningInsecureContent: true,
  // Use a unique partition to isolate cookies/sessions from other Electron apps
  // This ensures each Electron/Django project maintains its own separate session
  partition: 'persist:PROJECTNAME'  // Replace PROJECTNAME with your project's folder name
}
```

**Important**: Replace `PROJECTNAME` with your actual project folder name (same name used in Django settings). The partition name should be lowercase and match the project identifier used in the cookie names above.

## What This Fixes

- **Unique Session Cookies**: Each Django project uses different cookie names, preventing session conflicts
- **Separate Cookie Storage**: Each Electron app uses a different partition, isolating cookie storage
- **Persistent Sessions**: Sessions persist for 2 weeks, so you stay logged in across app restarts

## Example

If your project folder is named `myotherapp`, you would use:
- Django: `SESSION_COOKIE_NAME = 'myotherapp_sessionid'` and `CSRF_COOKIE_NAME = 'myotherapp_csrftoken'`
- Electron: `partition: 'persist:myotherapp'`

Make sure the project identifier (the part before `_sessionid` and `_csrftoken`) matches the partition name (the part after `persist:`).

Please implement these changes and verify that:
1. The session cookie names are unique to this project
2. The Electron partition name matches the project identifier
3. Sessions will now be isolated from other Electron/Django projects
