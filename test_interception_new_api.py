"""
Test script to explore the new interception-python API.
"""

import interception
import time

print("Available functions and classes in interception module:")
for item in dir(interception):
    if not item.startswith('_'):  # Skip private attributes
        print(f"- {item}")

print("\nTesting basic functionality:")

# Try to initialize interception
try:
    print("Setting up devices...")
    keyboard = interception.get_keyboard()
    mouse = interception.get_mouse()
    print(f"Keyboard: {keyboard}")
    print(f"Mouse: {mouse}")
    
    # Test key press
    print("\nTesting key press (will press 'a' after 3 seconds)...")
    print("Switch to a text editor now...")
    time.sleep(3)
    interception.press('a')
    
    # Test mouse click
    print("\nTesting mouse click (will left click after 3 seconds)...")
    print("Move your mouse to where you want to click...")
    time.sleep(3)
    interception.left_click()
    
    print("\nTest completed successfully!")
except Exception as e:
    print(f"Error during test: {e}")
