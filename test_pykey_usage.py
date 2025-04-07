"""
Test script to understand pyKey module functionality.
"""

import pyKey
import time
import inspect

def main():
    """Test pyKey module functionality."""
    print("Testing pyKey module functionality...")
    
    # Print available functions in pyKey module
    print("Available functions in pyKey module:")
    for name, obj in inspect.getmembers(pyKey):
        if inspect.isfunction(obj):
            try:
                print(f"  Function: {name}{inspect.signature(obj)}")
            except ValueError:
                print(f"  Function: {name}()")
    
    # Print pyKey module attributes
    print("\npyKey module attributes:")
    for attr_name in dir(pyKey):
        if not attr_name.startswith('_') and not callable(getattr(pyKey, attr_name)):
            attr = getattr(pyKey, attr_name)
            print(f"  {attr_name}: {attr}")
    
    # Print pyKey classes
    print("\npyKey classes:")
    for name, obj in inspect.getmembers(pyKey):
        if inspect.isclass(obj):
            print(f"  Class: {name}")
            # Print class methods
            for method_name, method_obj in inspect.getmembers(obj):
                if inspect.isfunction(method_obj) and not method_name.startswith('_'):
                    try:
                        print(f"    Method: {method_name}{inspect.signature(method_obj)}")
                    except ValueError:
                        print(f"    Method: {method_name}()")
    
    # Test basic functionality
    print("\nWaiting 3 seconds before testing key press/release...")
    time.sleep(3)
    
    # Try to use pyKey to press and release keys
    try:
        print("Testing key press/release...")
        
        # Try to create a key object
        if hasattr(pyKey, 'Key'):
            print("Using pyKey.Key class...")
            key = pyKey.Key()
            
            # Test arrow keys
            print("Pressing left arrow key...")
            key.press('left')
            time.sleep(0.5)
            print("Releasing left arrow key...")
            key.release('left')
            time.sleep(0.5)
            
            print("Pressing right arrow key...")
            key.press('right')
            time.sleep(0.5)
            print("Releasing right arrow key...")
            key.release('right')
        else:
            # Try direct functions
            print("Using direct functions...")
            
            # Test arrow keys
            print("Pressing left arrow key...")
            pyKey.press('left')
            time.sleep(0.5)
            print("Releasing left arrow key...")
            pyKey.release('left')
            time.sleep(0.5)
            
            print("Pressing right arrow key...")
            pyKey.press('right')
            time.sleep(0.5)
            print("Releasing right arrow key...")
            pyKey.release('right')
        
        # Test typing
        print("\nTyping 'Hello, World!'...")
        if hasattr(pyKey, 'write'):
            pyKey.write("Hello, World!")
        elif hasattr(pyKey, 'Key') and hasattr(pyKey.Key, 'write'):
            key = pyKey.Key()
            key.write("Hello, World!")
        else:
            print("No write function found, typing character by character...")
            for char in "Hello, World!":
                if hasattr(pyKey, 'Key'):
                    key = pyKey.Key()
                    key.tap(char)
                else:
                    pyKey.tap(char)
                time.sleep(0.1)
    
    except Exception as e:
        print(f"Error testing pyKey: {e}")
    
    print("\nTest complete.")

if __name__ == "__main__":
    main()
