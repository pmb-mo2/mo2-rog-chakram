#!/usr/bin/env python
"""
Simple script to check if pygame is installed correctly and can detect joysticks.
"""

import sys

def check_pygame():
    """Check if pygame is installed and print its version."""
    try:
        import pygame
        print(f"pygame is installed. Version: {pygame.version.ver}")
        return True
    except ImportError:
        print("pygame is NOT installed. Please install it with: pip install pygame==2.1.2")
        return False

def check_joysticks():
    """Check if any joysticks are connected and can be detected by pygame."""
    try:
        import pygame
        pygame.init()
        
        # Get the number of joysticks
        joystick_count = pygame.joystick.get_count()
        
        if joystick_count == 0:
            print("No joysticks detected. Please connect your Chakram X mouse and ensure it's in analog mode.")
            return False
        
        print(f"Detected {joystick_count} joystick(s):")
        
        # Initialize each joystick and print its information
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            
            # Get joystick information
            name = joystick.get_name()
            axes = joystick.get_numaxes()
            buttons = joystick.get_numbuttons()
            hats = joystick.get_numhats()
            
            print(f"  Joystick {i}:")
            print(f"    Name: {name}")
            print(f"    Axes: {axes}")
            print(f"    Buttons: {buttons}")
            print(f"    Hats: {hats}")
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"Error checking joysticks: {e}")
        return False

def main():
    """Main function."""
    print("Checking pygame installation...")
    pygame_installed = check_pygame()
    
    if pygame_installed:
        print("\nChecking for connected joysticks...")
        joysticks_detected = check_joysticks()
        
        if joysticks_detected:
            print("\nAll checks passed. You should be able to run the Chakram X Alternative Control System.")
            return 0
    
    print("\nSome checks failed. Please fix the issues before running the application.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
