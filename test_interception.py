#!/usr/bin/env python
"""
Test script for the Interception driver using interception-python.
This script demonstrates how to use the Interception driver to simulate mouse button presses.
"""

import sys
import time
from interception import *

def main():
    """Main function to test the Interception driver."""
    print("Interception Driver Test Script")
    print("==============================")
    print("This script will test the Interception driver by simulating mouse button presses.")
    print("Make sure the Interception driver is installed and running.")
    print()
    
    # Create an instance of the Interception context
    context = InterceptionContext()
    
    # Set the filter to capture all mouse and keyboard devices
    context.set_mouse_filter(InterceptionFilterMouseState.FILTER_MOUSE_ALL)
    context.set_keyboard_filter(InterceptionFilterKeyState.FILTER_KEY_ALL)
    
    # Find the first mouse device
    mouse_device = None
    for i in range(1, 11):  # Check devices 1-10
        if context.get_hardware_id(i).find(b"mouse") != -1:
            mouse_device = i
            break
    
    if mouse_device is None:
        print("Error: No mouse device found.")
        print("Make sure the Interception driver is installed correctly.")
        return 1
    
    print(f"Found mouse device at index {mouse_device}")
    print(f"Hardware ID: {context.get_hardware_id(mouse_device)}")
    print()
    
    # Test mouse button presses
    print("Testing mouse button presses...")
    print("1. Left mouse button")
    print("2. Middle mouse button")
    print("3. Right mouse button")
    print("4. All mouse buttons in sequence")
    print("5. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            print("Pressing left mouse button...")
            test_left_mouse_button(context, mouse_device)
        elif choice == "2":
            print("Pressing middle mouse button...")
            test_middle_mouse_button(context, mouse_device)
        elif choice == "3":
            print("Pressing right mouse button...")
            test_right_mouse_button(context, mouse_device)
        elif choice == "4":
            print("Pressing all mouse buttons in sequence...")
            test_all_mouse_buttons(context, mouse_device)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
    
    return 0

def test_left_mouse_button(context, device):
    """Test left mouse button press and release."""
    # Create a mouse stroke
    stroke = InterceptionMouseStroke()
    
    # Press left mouse button
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
    stroke.flags = 0
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    
    # Send the stroke
    context.send(device, stroke, 1)
    print("Left mouse button pressed")
    
    # Wait for a moment
    time.sleep(0.5)
    
    # Release left mouse button
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
    context.send(device, stroke, 1)
    print("Left mouse button released")

def test_middle_mouse_button(context, device):
    """Test middle mouse button press and release."""
    # Create a mouse stroke
    stroke = InterceptionMouseStroke()
    
    # Press middle mouse button
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN
    stroke.flags = 0
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    
    # Send the stroke
    context.send(device, stroke, 1)
    print("Middle mouse button pressed")
    
    # Wait for a moment
    time.sleep(0.5)
    
    # Release middle mouse button
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP
    context.send(device, stroke, 1)
    print("Middle mouse button released")

def test_right_mouse_button(context, device):
    """Test right mouse button press and release."""
    # Create a mouse stroke
    stroke = InterceptionMouseStroke()
    
    # Press right mouse button
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
    stroke.flags = 0
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    
    # Send the stroke
    context.send(device, stroke, 1)
    print("Right mouse button pressed")
    
    # Wait for a moment
    time.sleep(0.5)
    
    # Release right mouse button
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
    context.send(device, stroke, 1)
    print("Right mouse button released")

def test_all_mouse_buttons(context, device):
    """Test all mouse buttons in sequence."""
    # Create a mouse stroke
    stroke = InterceptionMouseStroke()
    stroke.flags = 0
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    
    # Left mouse button
    print("Testing left mouse button...")
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
    context.send(device, stroke, 1)
    time.sleep(0.2)
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
    context.send(device, stroke, 1)
    time.sleep(0.5)
    
    # Middle mouse button
    print("Testing middle mouse button...")
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN
    context.send(device, stroke, 1)
    time.sleep(0.2)
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP
    context.send(device, stroke, 1)
    time.sleep(0.5)
    
    # Right mouse button
    print("Testing right mouse button...")
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
    context.send(device, stroke, 1)
    time.sleep(0.2)
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
    context.send(device, stroke, 1)
    
    print("All mouse buttons tested")

if __name__ == "__main__":
    sys.exit(main())
