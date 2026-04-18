# AxoLexis Installer Documentation

## Overview

The updated installer is production-ready with:
- Progress UI showing each step
- Full logging to install.log
- Retry logic for pip install
- Validation at each stage
- Clean error handling

---

## Files

### post_install.ps1

The PowerShell script handles all post-installation tasks:

| Function | Purpose |
|----------|---------|
| `Initialize-Log` | Creates install.log in app directory |
| `Get-PythonPath` | Detects existing Python or finds in common locations |
| `Get-PythonVersion` | Validates Python version |
| `Install-Python` | Downloads and installs Python from python.org |
| `Validate-Python` | Tests Python works correctly |
| `New-AppVirtualEnvironment` | Creates venv in app directory |
| `Install-Dependencies` | Runs pip install with retries |
| `Create-Shortcuts` | Creates Desktop and Start Menu shortcuts |
| `Add-WindowsRegistry` | Registers in Add/Remove Programs |
| `Test-AppLaunch` | Verifies app can launch |
| `Complete-Installation` | Writes final summary |

### Key Features

1. **Progress Output** - Each step prints to console with clear headers
2. **Logging** - All actions logged to `{app}\install.log`
3. **Retries** - Pip install retries 3 times on failure
4. **Validation** - Python and venv validated before continuing
5. **Error Handling** - try/catch with meaningful error messages
6. **Exit Codes** - 0 on success, 1 on failure

### Example install.log

```
==============================================
AxoLexis Installation Log
==============================================
Install Path   : C:\Program Files\AxoLexis
Start Time    : 2024-01-15 10:30:00
Python URL   : https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe

[2024-01-15 10:30:01] Logger initialized
[2024-01-15 10:30:01] ==============================================
[2024-01-15 10:30:01] Starting AxoLexis Post-Install Configuration
[2024-01-15 10:30:01] ==============================================
[2024-01-15 10:30:02] Python not found in PATH, checking common locations...
[2024-01-15 10:30:02] Python not found in any common location
[2024-01-15 10:30:02] Python not found, installing Python 3.10...
[2024-01-15 10:30:05] Starting Python download and installation...
[2024-01-15 10:30:05] Downloading Python from https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe
[2024-01-15 10:30:45] Downloaded Python installer (25.62 MB)
[2024-01-15 10:30:46] Installing Python silently...
[2024-01-15 10:31:30] Python installation completed successfully
[2024-01-15 10:31:38] Python installed: C:\Users\[..]\AppData\Local\Programs\Python\Python310\python.exe (version 3.10)
[2024-01-15 10:31:38] Validating Python installation...
[2024-01-15 10:31:39] Python validation passed (version 3.10)
[2024-01-15 10:31:40] Creating virtual environment at C:\Program Files\AxoLexis\venv
[2024-01-15 10:31:45] Virtual environment created successfully
[2024-01-15 10:31:46] Installing dependencies from C:\Program Files\AxoLexis\requirements.txt
[2024-01-15 10:31:46] Pip install attempt 1 of 3
[2024-01-15 10:31:47] Upgrading pip...
[2024-01-15 10:31:52] Running: pip install -r requirements.txt --no-warn-script-location
[2024-01-15 10:35:20] Dependencies installed successfully on attempt 1
[2024-01-15 10:35:21] Validating installed packages...
[2024-01-15 10:35:25] Installed 17 packages
[2024-01-15 10:35:25]   [OK] PyQt6
[2024-01-15 10:35:25]   [OK] torch
[2024-01-15 10:35:25]   [OK] numpy
[2024-01-15 10:35:26] Creating shortcuts...
[2024-01-15 10:35:27] Created desktop shortcut
[2024-01-15 10:35:28] Created Start Menu shortcut
[2024-01-15 10:35:28] Created uninstall shortcut
[2024-01-15 10:35:29] Adding Windows registry entries...
[2024-01-15 10:35:30] Registry entries added
[2024-01-15 10:35:31] Testing application launch...
[2024-01-15 10:35:35] App launched successfully (PID: 1234)

==============================================
Installation Summary
==============================================
Status          : SUCCESS
End Time        : 2024-01-15 10:35:36
Error Message   : 
Install Path   : C:\Program Files\AxoLexis
```

### Error Log Example

```
[2024-01-15 10:30:02] Pip install attempt 1 of 3
[2024-01-15 10:30:03] Upgrading pip...
[2024-01-15 10:30:08] ERROR: Pip install attempt 1: Could not fetch latest package metadata
[2024-01-15 10:30:18] Waiting 10 seconds before retry...
[2024-01-15 10:30:28] Pip install attempt 2 of 3
[2024-01-15 10:32:15] Dependencies installed successfully on attempt 2

...

[2024-01-15 10:35:20] FATAL ERROR: Failed to install dependencies after 3 attempts
[2024-01-15 10:35:20] Stack trace: 
[2024-01-15 10:35:21] 

==============================================
Installation Summary
==============================================
Status          : FAILED
End Time       : 2024-01-15 10:35:21
Error Message : Failed to install dependencies after 3 attempts
Install Path  : C:\Program Files\AxoLexis
```

---

## Inno Setup Script Features

| Setting | Purpose |
|---------|---------|
| `SetupLogging=yes` | Enables Inno Setup's own logging |
| `PrivilegesRequired=admin` | Ensures registry writes succeed |
| `WizardStyle=modern` | Modern UI |
| `Wheel cache support` | Optional local wheel cache folder |
| Status message in `[Run]` | Shows progress during post-install |

---

## Wheel Cache (Optional)

To speed up installations on multiple machines:

1. Create a `wheel_cache` folder in the application directory
2. Download all wheels there:
```cmd
pip download -r requirements.txt -d wheel_cache
```

The installer will automatically use these if present.

---

## Build Instructions

```cmd
cd application

:: Build the PyInstaller executable first
pyinstaller axolexis.spec

:: Build the installer
iscc axolexis_setup.iss
```

Output: `application\installer\AxoLexis_Setup_v1.0.0.exe`

---

## Troubleshooting

### Enable Detailed Logging

Run installer with logging:
```cmd
AxoLexis_Setup_v1.0.0.exe /LOG="C:\axolexis_install.log"
```

### Manual Post-Install

Run the script manually:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Program Files\AxoLexis\post_install.ps1" -InstallPath "C:\Program Files\AxoLexis"
```

### Check install.log

Log is created at `{app}\install.log` - check this for detailed errors.

### Common Issues

| Issue | Solution |
|-------|----------|
| PowerShell blocked | Run with `-ExecutionPolicy Bypass` |
| Python download fails | Check internet/proxy settings |
| pip install timeout | Increase wait time in script |
| Missing shortcuts | Run as Administrator |
| App won't launch | Check install.log for errors |