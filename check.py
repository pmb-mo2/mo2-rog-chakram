#!/usr/bin/env python
"""
Utility to check for available joysticks and their axes.
This script helps diagnose issues with joystick detection and configuration.
"""

import os
import sys
import time
import pygame

def initialize_pygame():
    """Initialize pygame with error handling."""
    try:
        pygame.init()
        print(f"pygame initialized successfully. Version: {pygame.version.ver}")
        
        # Check SDL version
        try:
            sdl_version = pygame.get_sdl_version()
            print(f"SDL Version: {sdl_version[0]}.{sdl_version[1]}.{sdl_version[2]}")
        except (pygame.error, AttributeError) as e:
            print(f"Error getting SDL version: {e}")
        
        return True
    except Exception as e:
        print(f"Failed to initialize pygame: {e}")
        return False

def check_joysticks():
    """Check for available joysticks and their properties."""
    try:
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            print("No joysticks found. Please connect a joystick and try again.")
            return False
        
        print(f"\nFound {joystick_count} joystick(s):")
        
        for i in range(joystick_count):
            try:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                name = joystick.get_name()
                guid = joystick.get_guid() if hasattr(joystick, 'get_guid') else "N/A"
                instance_id = joystick.get_instance_id() if hasattr(joystick, 'get_instance_id') else "N/A"
                
                print(f"\nJoystick {i}: {name}")
                print(f"  GUID: {guid}")
                print(f"  Instance ID: {instance_id}")
                
                # Get joystick capabilities
                num_axes = joystick.get_numaxes()
                num_buttons = joystick.get_numbuttons()
                num_hats = joystick.get_numhats()
                num_balls = joystick.get_numballs() if hasattr(joystick, 'get_numballs') else 0
                
                print(f"  Axes: {num_axes}")
                print(f"  Buttons: {num_buttons}")
                print(f"  Hats: {num_hats}")
                print(f"  Trackballs: {num_balls}")
                
                # Check axis values
                if num_axes > 0:
                    print("\n  Current axis values:")
                    for axis in range(num_axes):
                        try:
                            value = joystick.get_axis(axis)
                            print(f"    Axis {axis}: {value:.6f}")
                        except pygame.error as e:
                            print(f"    Error reading axis {axis}: {e}")
                
                # Check button values
                if num_buttons > 0:
                    print("\n  Current button states:")
                    for button in range(num_buttons):
                        try:
                            value = joystick.get_button(button)
                            print(f"    Button {button}: {value}")
                        except pygame.error as e:
                            print(f"    Error reading button {button}: {e}")
                
                # Check hat values
                if num_hats > 0:
                    print("\n  Current hat states:")
                    for hat in range(num_hats):
                        try:
                            value = joystick.get_hat(hat)
                            print(f"    Hat {hat}: {value}")
                        except pygame.error as e:
                            print(f"    Error reading hat {hat}: {e}")
                
                # Check for Chakram X
                if "CHAKRAM" in name.upper():
                    print("\n  This appears to be a Chakram X joystick!")
                    
                    # Check if it has enough axes
                    if num_axes < 2:
                        print("  WARNING: This Chakram X joystick has fewer than 2 axes, which may cause issues.")
                    else:
                        print("  This Chakram X joystick has the required number of axes.")
                
            except pygame.error as e:
                print(f"Error initializing joystick {i}: {e}")
        
        return True
    except pygame.error as e:
        print(f"Error checking joysticks: {e}")
        return False

def monitor_joystick_movement(joystick_id=0, duration=10):
    """Monitor joystick movement for a specified duration."""
    try:
        if pygame.joystick.get_count() <= joystick_id:
            print(f"Joystick {joystick_id} not found.")
            return False
        
        joystick = pygame.joystick.Joystick(joystick_id)
        joystick.init()
        
        print(f"\nMonitoring joystick {joystick_id} ({joystick.get_name()}) for {duration} seconds.")
        print("Move the joystick to see axis values change in real-time.")
        print("Press Ctrl+C to stop monitoring early.")
        
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            while time.time() < end_time:
                # Process events to get fresh joystick data
                pygame.event.pump()
                
                # Get axis values
                axes_values = []
                for axis in range(joystick.get_numaxes()):
                    value = joystick.get_axis(axis)
                    axes_values.append(f"Axis {axis}: {value:+.2f}")
                
                # Clear line and print current values
                sys.stdout.write("\r" + " " * 80)  # Clear line
                sys.stdout.write("\r" + " | ".join(axes_values[:4]))  # Show first 4 axes
                sys.stdout.flush()
                
                time.sleep(0.1)
            
            print("\nMonitoring complete.")
            return True
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            return True
    except pygame.error as e:
        print(f"Error monitoring joystick: {e}")
        return False

def main():
    """Main function."""
    # Set environment variable for background joystick events
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    
    print("Chakram X Joystick Check Utility")
    print("================================")
    
    # Initialize pygame
    if not initialize_pygame():
        return 1
    
    # Check for joysticks
    if not check_joysticks():
        pygame.quit()
        return 1
    
    # Ask if user wants to monitor a joystick
    try:
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            print("\nWould you like to monitor a joystick's movement? (y/n)")
            response = input("> ").strip().lower()
            
            if response.startswith("y"):
                joystick_id = 0
                if joystick_count > 1:
                    print(f"Which joystick would you like to monitor? (0-{joystick_count-1})")
                    try:
                        joystick_id = int(input("> ").strip())
                        if joystick_id < 0 or joystick_id >= joystick_count:
                            print(f"Invalid joystick ID. Using default (0).")
                            joystick_id = 0
                    except ValueError:
                        print("Invalid input. Using default joystick (0).")
                
                monitor_joystick_movement(joystick_id)
    except KeyboardInterrupt:
        print("\nCheck utility stopped by user.")
    
    # Clean up
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
