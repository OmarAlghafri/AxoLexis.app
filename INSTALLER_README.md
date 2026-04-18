# AxoLexis Lightweight Installer - Build Instructions

## Overview

This lightweight installer uses Inno Setup but does NOT bundle Python or any dependencies. Instead, the post-install script checks for Python, downloads it if needed, creates a virtual environment, and installs dependencies at runtime.

## Files Created

1. **axolexis_setup.iss** - Inno Setup script (~2KB, no bundled Python)
2. **post_install.ps1** - PowerShell post-install script (~8KB)
3. **requirements.txt** - Already exists in the application folder

## Estimated Installer Size

- **~500KB - 2MB** (only application files, no Python/runtime)
- Python (~25MB) and pip dependencies (~500MB-2GB) are downloaded at install time

## Build Steps

### 1. Prerequisites
- Install [Inno Setup](https://jrsoftware.org/isinfo.php) 6.0 or later
- Have PyInstaller build completed: `pyinstaller axolexis.spec`

### 2. Build the Installer
```cmd
cd application
iscc axolexis_setup.iss
```

Output will be in `application\installer\AxoLexis_Setup_v1.0.0.exe`

### 3. Test Installation
1. Run the installer on a clean Windows 10/11 machine
2. The post-install script will:
   - Check for Python 3.10+
   - Download and install Python if not found
   - Create `venv` in the app directory
   - Install requirements.txt via pip
   - Create Desktop and Start Menu shortcuts

## Post-Install Script Features

- **Python Detection**: Checks multiple common install locations
- **Automatic Download**: Downloads Python from python.org if missing
- **Virtual Environment**: Creates isolated venv in app directory
- **Dependency Installation**: Runs `pip install -r requirements.txt`
- **Shortcut Creation**: Creates Desktop and Start Menu shortcuts
- **Windows Registry**: Registers in Add/Remove Programs

## Customization

### Change Python Version
Edit `post_install.ps1` and update:
```powershell
$MinPythonVersion = [version]"3.10"
$PythonDownloadUrl = "https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe"
```

### Change Python Download URL
For latest Python 3.10:
```powershell
$PythonDownloadUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
```

## Troubleshooting

### Installation Fails with PowerShell Error
Run installer with:
```cmd
AxoLexis_Setup_v1.0.0.exe /LOG="C:\install.log"
```
Then check `C:\install.log` for details.

### Python Download Fails
- Check internet connection
- Try manual Python installation first
- The script will use existing Python if available

### pip Install Timeout
Dependencies like PyTorch and transformers are large. This can take 10-30 minutes on slow connections.

## Architecture Notes

- Installer is x64-only (x64compatible handles both 64-bit and WOW64)
- Python x64 is installed
- Works on Windows 10 (1809+) and Windows 11

## Cleanup on Uninstall

The `[UninstallDelete]` section removes the entire application folder including the venv.