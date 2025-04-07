"""
Test script to understand keyboard module functionality.
"""

import keyboard
import time
import inspect

def main():
    """Test keyboard module functionality."""
    print("Testing keyboard module functionality...")
    
    # Print available functions in keyboard module
    print("Available functions in keyboard module:")
    for name, obj in inspect.getmembers(keyboard):
        if inspect.isfunction(obj):
            try:
                print(f"  Function: {name}{inspect.signature(obj)}")
            except ValueError:
                print(f"  Function: {name}()")
    
    # Print keyboard module attributes
    print("\nKeyboard module attributes:")
    for attr_name in dir(keyboard):
        if not attr_name.startswith('_') and not callable(getattr(keyboard, attr_name)):
            attr = getattr(keyboard, attr_name)
            print(f"  {attr_name}: {attr}")
    
    # Test basic functionality
    print("\nWaiting 3 seconds before testing key press/release...")
    time.sleep(3)
    
    # Press and release arrow keys
    print("Pressing left arrow key...")
    keyboard.press('left')
    time.sleep(0.5)
    print("Releasing left arrow key...")
    keyboard.release('left')
    time.sleep(0.5)
    
    print("Pressing right arrow key...")
    keyboard.press('right')
    time.sleep(0.5)
    print("Releasing right arrow key...")
    keyboard.release('right')
    
    # Test typing
    print("\nTyping 'Hello, World!'...")
    keyboard.write("Hello, World!")
    
    print("\nTest complete.")

if __name__ == "__main__":
    main()
