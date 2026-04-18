#!/usr/bin/env python
"""
AxoLexis Bootstrap Launcher
Small stub that runs on first launch to set up the environment
"""

import sys
import os
import subprocess
import shutil

APP_NAME = "AxoLexis"
MIN_PYTHON = (3, 10)

def log(msg):
    print(f"[AxoLexis] {msg}")

def get_python():
    """Find system Python or create simple error"""
    # Check PATH
    python_cmd = shutil.which("python")
    if python_cmd:
        return python_cmd
    
    # Check common locations on Windows
    if os.name == 'nt':
        common_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python310', 'python.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', 'Programs', 'Python', 'Python39', 'python.exe')),
            r"C:\Python310\python.exe",
            r"C:\Python39\python.exe",
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    
    return None

def check_python_version(python_path):
    """Check if Python meets minimum version"""
    try:
        result = subprocess.run(
            [python_path, '--version'], 
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        if 'Python' in output:
            version_str = output.replace('Python', '').strip().split('.')
            version = tuple(int(x) for x in version_str[:2])
            return version >= MIN_PYTHON
    except:
        pass
    return False

def create_venv(venv_path, python_path):
    """Create virtual environment"""
    log(f"Creating virtual environment...")
    subprocess.run([python_path, '-m', 'venv', venv_path], check=True)
    log("Virtual environment created")

def install_dependencies(venv_path):
    """Install requirements via pip"""
    pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', 'pip')
    
    app_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(app_dir, 'requirements.txt')
    
    if os.path.exists(req_file):
        log("Installing dependencies (this may take several minutes)...")
        subprocess.run([pip_path, 'install', '-r', req_file], check=True)
        log("Dependencies installed")

def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(app_dir, 'venv')
    
    # Check if already set up
    if os.path.exists(venv_path):
        venv_python = os.path.join(venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', 'python')
        if os.path.exists(venv_python):
            # Run main application
            main_script = os.path.join(app_dir, 'main_enhanced.py')
            subprocess.run([venv_python, main_script] + sys.argv[1:])
            return
    
    # Setup required
    log("First-time setup starting...")
    
    python_path = get_python()
    if not python_path:
        print("ERROR: Python 3.10+ not found. Please install Python from https://python.org")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not check_python_version(python_path):
        print(f"ERROR: Python 3.10+ required. Found version too old.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    create_venv(venv_path, python_path)
    install_dependencies(venv_path)
    
    # Launch application
    log("Launching AxoLexis...")
    venv_python = os.path.join(venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', 'python')
    main_script = os.path.join(app_dir, 'main_enhanced.py')
    subprocess.run([venv_python, main_script] + sys.argv[1:])

if __name__ == '__main__':
    main()