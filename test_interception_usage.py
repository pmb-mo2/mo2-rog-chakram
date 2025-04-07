"""
Test script for demonstrating the interception-python library for keyboard and mouse input.
This script shows how to use the win_input_interception.py module to simulate keyboard and mouse events.
"""

import time
import sys
import os
from src.win_input_interception import (
    initialize, cleanup, 
    key_down, key_up, press_key,
    left_mouse_down, left_mouse_up, click_left_mouse,
    middle_mouse_down, middle_mouse_up, click_middle_mouse,
    right_mouse_down, right_mouse_up, click_right_mouse,
    send_sector_change
)

def test_keyboard_input():
    """Test basic keyboard input functions."""
    print("Testing keyboard input...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Test individual key presses
    print("Testing individual key presses...")
    for key in ['a', 'b', 'c', 'd', 'e']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.5)
    
    # Test key down and up separately
    print("Testing key down and up separately...")
    key_down('shift')
    time.sleep(0.5)
    
    for key in ['h', 'e', 'l', 'l', 'o']:
        press_key(key)
        time.sleep(0.2)
    
    key_up('shift')
    time.sleep(0.5)
    
    # Test arrow keys
    print("Testing arrow keys...")
    for key in ['left', 'up', 'right', 'down']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.5)
    
    print("Keyboard input test complete.")

def test_mouse_input():
    """Test basic mouse input functions."""
    print("Testing mouse input...")
    
    # Wait for user to switch to a window where mouse clicks are visible
    print("Switch to a window where mouse clicks are visible in 3 seconds...")
    time.sleep(3)
    
    # Test left mouse button
    print("Testing left mouse button...")
    print("Left mouse down")
    left_mouse_down()
    time.sleep(0.5)
    
    print("Left mouse up")
    left_mouse_up()
    time.sleep(0.5)
    
    print("Left mouse click")
    click_left_mouse()
    time.sleep(0.5)
    
    # Test right mouse button
    print("Testing right mouse button...")
    print("Right mouse down")
    right_mouse_down()
    time.sleep(0.5)
    
    print("Right mouse up")
    right_mouse_up()
    time.sleep(0.5)
    
    print("Right mouse click")
    click_right_mouse()
    time.sleep(0.5)
    
    # Test middle mouse button
    print("Testing middle mouse button...")
    print("Middle mouse down")
    middle_mouse_down()
    time.sleep(0.5)
    
    print("Middle mouse up")
    middle_mouse_up()
    time.sleep(0.5)
    
    print("Middle mouse click")
    click_middle_mouse()
    time.sleep(0.5)
    
    print("Mouse input test complete.")

def test_sector_change():
    """Test the sector change function."""
    print("Testing sector change...")
    
    # Wait for user to switch to a game or application
    print("Switch to a game or application in 3 seconds...")
    time.sleep(3)
    
    # Test with keyboard cancel key
    print("Testing sector change with keyboard cancel key...")
    print("Changing from 'left' to 'right' using 'esc' as cancel key")
    send_sector_change('esc', 'left', 'right')
    time.sleep(1)
    
    # Test with middle mouse button as cancel
    print("Testing sector change with middle mouse button...")
    print("Changing from 'up' to 'down' using middle mouse button")
    send_sector_change('middle_mouse', 'up', 'down')
    time.sleep(1)
    
    print("Sector change test complete.")

def main():
    """Main function to run all tests."""
    print("Starting interception-python input tests...")
    
    # Initialize the input module
    if not initialize():
        print("Failed to initialize input module. Exiting.")
        return
    
    try:
        # Run the tests
        test_keyboard_input()
        time.sleep(1)
        
        test_mouse_input()
        time.sleep(1)
        
        test_sector_change()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        # Clean up
        cleanup()
    
    print("All tests completed.")

if __name__ == "__main__":
    main()
