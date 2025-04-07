#!/usr/bin/env python
"""
Script to help fix common pygame installation issues.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check the Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("WARNING: Python 3.6 or higher is recommended for pygame 2.1.2")
        return False
    
    return True

def check_pip():
    """Check if pip is installed and get its version."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                               capture_output=True, text=True, check=True)
        print(f"pip is installed: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("pip is NOT installed or not working properly")
        return False

def check_pygame():
    """Check if pygame is installed and get its version."""
    try:
        import pygame
        print(f"pygame is installed. Version: {pygame.version.ver}")
        
        if pygame.version.ver != "2.1.2":
            print(f"WARNING: The installed pygame version ({pygame.version.ver}) is not 2.1.2")
            return False
        
        return True
    except ImportError:
        print("pygame is NOT installed")
        return False

def install_pygame():
    """Install pygame 2.1.2."""
    print("\nAttempting to install pygame 2.1.2...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pygame==2.1.2"], check=True)
        print("pygame 2.1.2 installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing pygame: {e}")
        return False

def uninstall_pygame():
    """Uninstall pygame."""
    print("\nAttempting to uninstall pygame...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pygame"], check=True)
        print("pygame uninstalled successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error uninstalling pygame: {e}")
        return False

def install_dependencies():
    """Install dependencies required for pygame on the current platform."""
    system = platform.system()
    
    if system == "Linux":
        print("\nInstalling pygame dependencies for Linux...")
        print("You may need to enter your password for sudo commands.")
        
        try:
            # Common dependencies for pygame on Linux
            dependencies = [
                "python3-dev", "python3-numpy", "python3-setuptools",
                "libsdl2-dev", "libsdl2-image-dev", "libsdl2-mixer-dev",
                "libsdl2-ttf-dev", "libfreetype6-dev", "libportmidi-dev"
            ]
            
            # Use apt-get if available
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y"] + dependencies, check=True)
            
            print("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            print("You may need to install the dependencies manually.")
            return False
    elif system == "Darwin":  # macOS
        print("\nInstalling pygame dependencies for macOS...")
        
        try:
            # Check if Homebrew is installed
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            
            # Install dependencies using Homebrew
            subprocess.run(["brew", "install", "sdl2", "sdl2_image", "sdl2_mixer", "sdl2_ttf", "portmidi"], check=True)
            
            print("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Homebrew is not installed or an error occurred.")
            print("You may need to install Homebrew (https://brew.sh/) and then install the dependencies manually.")
            return False
    elif system == "Windows":
        print("\nOn Windows, pygame should install all required dependencies automatically.")
        return True
    else:
        print(f"Unsupported platform: {system}")
        return False

def main():
    """Main function."""
    print("=== Pygame Installation Fixer ===\n")
    
    print("Checking system information...")
    system = platform.system()
    print(f"Operating System: {platform.platform()}")
    
    print("\nChecking Python installation...")
    python_ok = check_python_version()
    
    print("\nChecking pip installation...")
    pip_ok = check_pip()
    
    if not pip_ok:
        print("\nPlease install pip before continuing.")
        return 1
    
    print("\nChecking pygame installation...")
    pygame_ok = check_pygame()
    
    if pygame_ok:
        print("\npygame 2.1.2 is already installed correctly.")
        return 0
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Install pygame 2.1.2")
    print("2. Uninstall pygame and then install pygame 2.1.2")
    print("3. Install dependencies and then install pygame 2.1.2")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        install_pygame()
    elif choice == "2":
        if uninstall_pygame():
            install_pygame()
    elif choice == "3":
        if install_dependencies():
            install_pygame()
    elif choice == "4":
        print("Exiting...")
        return 0
    else:
        print("Invalid choice. Exiting...")
        return 1
    
    # Check if pygame is now installed correctly
    print("\nChecking if pygame is now installed correctly...")
    pygame_ok = check_pygame()
    
    if pygame_ok:
        print("\nSuccess! pygame 2.1.2 is now installed correctly.")
        return 0
    else:
        print("\nThere was a problem installing pygame 2.1.2.")
        print("You may need to try a different approach or install it manually.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
