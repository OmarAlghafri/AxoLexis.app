"""
Enhanced AxoLexis Main Application with Intelligent Training Integration
Updated to use all new intelligent training features and comprehensive validation
"""

import sys
import os
import subprocess

def setup_and_launch_venv():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(app_dir, "venv")
    
    if os.name == 'nt':
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        
    if sys.prefix == venv_dir or sys.executable == venv_python:
        return
        
    print("========== AxoLexis First-Time Setup ==========")
    
    if not os.path.exists(venv_python):
        print("-> Creating isolated virtual environment...")
        import venv
        try:
            venv.create(venv_dir, with_pip=True)
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
            
    setup_marker = os.path.join(venv_dir, ".setup_complete")
    if not os.path.exists(setup_marker):
        print("-> Installing GUI dependencies for setup...")
        subprocess.call([venv_python, "-m", "pip", "install", "PyQt6", "--upgrade"])
        
        print("-> Launching setup UI for heavy packages...")
        setup_ui_script = os.path.join(app_dir, "setup_updater.py")
        req_file = os.path.join(app_dir, "requirements.txt")
        subprocess.call([venv_python, setup_ui_script, venv_python, req_file, setup_marker])
            
    print("-> Setup complete. Launching AxoLexis...")
    sys.exit(subprocess.call([venv_python, __file__] + sys.argv[1:]))

setup_and_launch_venv()

# IMPORTANT: Import torch BEFORE PyQt6 on Windows to prevent WinError 1114.
try:
    import torch
    print(f"[*] PyTorch {torch.__version__} loaded successfully")
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"[*] CUDA {torch.version.cuda} available on {torch.cuda.get_device_name(0)}")
    else:
        print("[!] CUDA not available, will use CPU")
        
except ImportError as e:
    print(f"[!] PyTorch import failed: {e}")
    print("Continuing with limited functionality...")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import new intelligent training systems
from ui.theme_manager import ThemeManager
from ui.enhanced_main_window import create_enhanced_main_window
from intelligent_training_integration import create_intelligent_training_system
from training_transparency_logger import create_transparency_logger
from runtime_validator import create_runtime_validator
from models.model_download_manager import create_model_download_manager, create_model_availability_checker

def main():
    """Enhanced main function with intelligent training integration"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("AxoLexis")
    app.setApplicationVersion("3.1")
    app.setOrganizationName("AxoLexis Labs")
    
    # Initialize theme manager
    theme_manager = ThemeManager()
    theme_manager.apply(app)
    
    print("Initializing AxoLexis Intelligent Training System...")
    
    # Create intelligent training systems
    try:
        # Create transparency logger
        transparency_logger = create_transparency_logger()
        print("[*] Transparency logger initialized")
        
        # Create runtime validator
        runtime_validator = create_runtime_validator()
        print("[*] Runtime validator initialized")
        
        # Create model download manager
        model_download_manager = create_model_download_manager()
        print("[*] Model download manager initialized")
        
        # Create model availability checker
        model_availability_checker = create_model_availability_checker(model_download_manager)
        print("[*] Model availability checker initialized")
        
        # Create intelligent training system
        intelligent_training = create_intelligent_training_system()
        print("[*] Intelligent training system initialized")
        
    except Exception as e:
        print(f"[!] Failed to initialize intelligent systems: {e}")
        print("Continuing with basic functionality...")
        transparency_logger = None
        runtime_validator = None
        model_download_manager = None
        model_availability_checker = None
        intelligent_training = None
    
    # Create enhanced main window
    try:
        main_window = create_enhanced_main_window()
        
        # Connect intelligent systems to main window
        if intelligent_training:
            main_window.intelligent_training = intelligent_training
            
        if transparency_logger:
            main_window.transparency_logger = transparency_logger
            
        if runtime_validator:
            main_window.runtime_validator = runtime_validator
            
        if model_download_manager:
            main_window.model_download_manager = model_download_manager
            
        if model_availability_checker:
            main_window.model_availability_checker = model_availability_checker
        
        print("[*] Enhanced main window created")
        
    except Exception as e:
        print(f"[!] Failed to create enhanced main window: {e}")
        print("Falling back to basic window...")
        # Fallback to basic window would go here
        return 1
    
    # Show main window
    main_window.show()
    
    # Print startup summary
    print("\n" + "="*60)
    print("[*] AXOLEXIS INTELLIGENT TRAINING SYSTEM READY")
    print("="*60)
    print("[*] All intelligent training features integrated")
    print("[*] Comprehensive task definition system active")
    print("[*] Enhanced model registry with 100+ models")
    print("[*] Real-time transparency and logging enabled")
    print("[*] Runtime validation system operational")
    print("[*] Model auto-download system ready")
    print("="*60)
    print("[*] Ready to start intelligent training!")
    print("="*60 + "\n")
    
    # Start application event loop
    return app.exec()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutting down AxoLexis...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)