#!/usr/bin/env python
"""
AxoLexis Launcher
Simple bootstrap - creates venv and launches app on first run
"""

import sys
import os
import subprocess
import shutil
import textwrap

APP_NAME = "AxoLexis"
MIN_PYTHON = (3, 10)

def log(msg, *args):
    print(f"[AxoLexis] {msg}" % args if args else f"[AxoLexis] {msg}")

def get_python():
    """Find system Python"""
    python_cmd = shutil.which("python")
    if python_cmd:
        return python_cmd
    
    if os.name == 'nt':
        for ver in ['310', '311', '312']:
            for loc in [os.environ.get('LOCALAPPDATA', ''), os.environ.get('PROGRAMFILES', 'C:\\Program Files')]:
                for arch in ['', ' (x86)']:
                    base = os.path.join(loc, f'Python{ver}', 'python.exe')
                    if os.path.exists(base):
                        return base
    
    return None

def check_python_version(python_path):
    """Check Python meets minimum version"""
    try:
        result = subprocess.run([python_path, '--version'], capture_output=True, text=True)
        version_str = result.stdout.replace('Python', '').strip().split('.')
        version = tuple(int(x) for x in version_str[:2])
        return version >= MIN_PYTHON
    except:
        return False

def create_venv(venv_path, python_path):
    """Create virtual environment"""
    log("Creating virtual environment...")
    subprocess.run([python_path, '-m', 'venv', venv_path], check=True)
    log("Virtual environment created at venv/")

def install_dependencies(venv_path):
    """Install requirements via pip"""
    script_dir = 'Scripts' if os.name == 'nt' else 'bin'
    pip_path = os.path.join(venv_path, script_dir, 'pip.exe' if os.name == 'nt' else 'pip')
    
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    
    if os.path.exists(req_file):
        log("Installing dependencies (this may take several minutes)...")
        
        # First upgrade pip
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], capture_output=True)
        
        # Install requirements
        proc = subprocess.Popen([pip_path, 'install', '-r', req_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            print(line.decode(), end='')
        
        if proc.wait() != 0:
            log("ERROR: Failed to install dependencies")
            return False
        
        log("Dependencies installed successfully")
        return True
    
    log("WARNING: requirements.txt not found")
    return False

def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(app_dir, 'venv')
    script_dir = 'Scripts' if os.name == 'nt' else 'bin'
    venv_python = os.path.join(venv_path, script_dir, 'python.exe' if os.name == 'nt' else 'python')
    
    # Check if already set up
    if os.path.exists(venv_path) and os.path.exists(venv_python):
        log("Launching AxoLexis...")
        main_script = os.path.join(app_dir, 'main_enhanced.py')
        subprocess.run([venv_python, main_script] + sys.argv[1:])
        return
    
    # First-time setup
    log("=" * 50)
    log("First-time setup - this may take several minutes")
    log("=" * 50)
    
    python_path = get_python()
    if not python_path:
        print(textwrap.dedent("""
            ERROR: Python 3.10+ not found.
            
            Please install Python from https://python.org
            Make sure to check "Add Python to PATH" during installation.
        """))
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not check_python_version(python_path):
        print(f"ERROR: Python 3.10+ required. Please upgrade Python.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    log(f"Using Python at: {python_path}")
    
    create_venv(venv_path, python_path)
    
    if not install_dependencies(venv_path):
        print(textwrap.dedent("""
            ERROR: Failed to install dependencies.
            Check your internet connection and try again.
        """))
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Launch application
    log("Launching AxoLexis...")
    main_script = os.path.join(app_dir, 'main_enhanced.py')
    subprocess.run([venv_python, main_script] + sys.argv[1:])

if __name__ == '__main__':
    main()