#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import venv
import shutil
from pathlib import Path

# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message, color=Colors.BLUE):
    """Print a status message with color"""
    print(f"{color}{message}{Colors.END}")

def print_success(message):
    """Print a success message in green"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print an error message in red"""
    print(f"{Colors.RED}✗ ERROR: {message}{Colors.END}")

def print_warning(message):
    """Print a warning message in yellow"""
    print(f"{Colors.YELLOW}⚠ WARNING: {message}{Colors.END}")

def run_command(cmd, cwd=None, shell=False):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True, 
            cwd=cwd,
            shell=shell
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print_error(f"Error message: {e.stderr.strip()}")
        return None

def is_venv_activated():
    """Check if a virtual environment is currently activated"""
    return (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def get_python_executable():
    """Get the appropriate Python executable name"""
    if platform.system() == "Windows":
        return "python"
    else:
        return "python3"

def setup_virtual_environment(venv_path):
    """Create a virtual environment if it doesn't exist"""
    if os.path.exists(venv_path):
        print_status(f"Virtual environment found at {venv_path}")
        return True
    
    print_status(f"Creating virtual environment at {venv_path}...")
    try:
        venv.create(venv_path, with_pip=True)
        print_success(f"Virtual environment created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {str(e)}")
        return False

def get_venv_activate_command(venv_path):
    """Get the platform-specific command to activate the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "activate")
    else:
        return os.path.join(venv_path, "bin", "activate")

def get_venv_python(venv_path):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def get_venv_pip(venv_path):
    """Get the path to the pip executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_path, "bin", "pip")

def install_packages(venv_path):
    """Install required packages in the virtual environment"""
    pip_executable = get_venv_pip(venv_path)
    
    # Check if pip exists
    if not os.path.exists(pip_executable):
        print_error(f"Pip not found at {pip_executable}")
        return False
    
    # Install packages
    packages = ["pycryptodome", "pillow"]
    print_status(f"Installing packages: {', '.join(packages)}")
    
    for package in packages:
        print_status(f"Installing {package}...")
        cmd = [pip_executable, "install", package]
        result = run_command(cmd)
        
        if result is None:
            print_error(f"Failed to install {package}")
            return False
        else:
            print_success(f"Successfully installed {package}")
    
    return True

def check_installation(venv_path):
    """Check if the installation was successful by importing the modules"""
    python_executable = get_venv_python(venv_path)
    
    print_status("Verifying installation...")
    
    # Check pycryptodome
    cmd = [python_executable, "-c", "from Crypto.Cipher import AES; print('PyCryptodome successfully installed')"]
    result = run_command(cmd)
    
    if result is None:
        print_error("PyCryptodome installation verification failed")
        return False
    else:
        print_success("PyCryptodome successfully installed and verified")
    
    # Check pillow
    cmd = [python_executable, "-c", "from PIL import Image; print('Pillow successfully installed')"]
    result = run_command(cmd)
    
    if result is None:
        print_error("Pillow installation verification failed")
        return False
    else:
        print_success("Pillow successfully installed and verified")
    
    return True

def copy_key_file():
    """Copy the AES key file to the expected location if needed"""
    source_key = os.path.join('Ransomware', 'aes128_key.bin')
    dest_key = 'aes128_key.bin'
    
    if not os.path.exists(source_key):
        print_warning(f"AES key file not found at {source_key}")
        return
    
    if not os.path.exists(dest_key):
        try:
            shutil.copy2(source_key, dest_key)
            print_success(f"Copied AES key file to {dest_key}")
        except Exception as e:
            print_error(f"Failed to copy AES key file: {str(e)}")
    else:
        print_status(f"AES key file already exists at {dest_key}")

def print_activation_instructions(venv_path):
    """Print instructions for activating the virtual environment"""
    activate_cmd = get_venv_activate_command(venv_path)
    
    print("\n" + "="*80)
    print_status("SETUP COMPLETE", color=Colors.GREEN)
    print("="*80)
    
    print(f"\nTo activate the virtual environment manually, run:")
    
    if platform.system() == "Windows":
        print(f"\n{Colors.YELLOW}    {activate_cmd}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}    source {activate_cmd}{Colors.END}")
    
    print(f"\nTo run the demo after activation, use:")
    print(f"\n{Colors.YELLOW}    python main.py{Colors.END}")
    
    print(f"\nOr to run without manual activation, use:")
    python_path = get_venv_python(venv_path)
    print(f"\n{Colors.YELLOW}    {python_path} main.py{Colors.END}")
    
    print("\n" + "="*80)

def create_launcher_script(venv_path):
    """Create a launcher script to run the program with the correct environment"""
    venv_python = get_venv_python(venv_path)
    
    if platform.system() == "Windows":
        launcher_path = "run_demo.bat"
        with open(launcher_path, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'echo Running Demo with Python virtual environment...\n')
            f.write(f'"{venv_python}" main.py\n')
            f.write(f'pause\n')
    else:
        launcher_path = "run_demo.sh"
        with open(launcher_path, 'w') as f:
            f.write(f'#!/bin/bash\n')
            f.write(f'echo "Running Demo with Python virtual environment..."\n')
            f.write(f'"{venv_python}" main.py\n')
        
        # Make the launcher executable on Unix
        try:
            os.chmod(launcher_path, 0o755)
        except Exception as e:
            print_warning(f"Could not make launcher script executable: {str(e)}")
    
    print_success(f"Created launcher script: {launcher_path}")
    
    return launcher_path

def main():
    """Main setup function"""
    print("\n" + "="*80)
    print_status(f"{Colors.BOLD}DemoGUI-2.0 Setup{Colors.END}", color=Colors.GREEN)
    print("="*80 + "\n")
    
    # Check Python version
    python_version = platform.python_version()
    print_status(f"Python version: {python_version}")
    
    if int(python_version.split('.')[0]) < 3:
        print_error("Python 3.x is required")
        sys.exit(1)
    
    # Define virtual environment path
    # Use a persistent location on Linux/Kali
    if platform.system() == "Windows":
        venv_path = os.path.join(os.getcwd(), "venv")
    else:
        # On Linux/Kali, use a home directory location that persists across reboots
        home_dir = os.path.expanduser("~")
        venv_path = os.path.join(home_dir, ".demo_gui_venv")
    
    # Set up virtual environment
    if not setup_virtual_environment(venv_path):
        print_error("Failed to set up virtual environment")
        sys.exit(1)
    
    # Install required packages
    if not install_packages(venv_path):
        print_error("Failed to install required packages")
        sys.exit(1)
    
    # Verify installation
    if not check_installation(venv_path):
        print_error("Installation verification failed")
        sys.exit(1)
    
    # Copy key file if needed
    copy_key_file()
    
    # Create launcher script
    launcher_path = create_launcher_script(venv_path)
    
    # Print instructions
    print_activation_instructions(venv_path)
    
    # Print how to run the launcher
    print(f"\nYou can now run the demo using the launcher script:")
    if platform.system() == "Windows":
        print(f"\n{Colors.YELLOW}    {launcher_path}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}    ./{launcher_path}{Colors.END}")

if __name__ == "__main__":
    main()

