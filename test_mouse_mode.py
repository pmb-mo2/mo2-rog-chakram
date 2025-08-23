#!/usr/bin/env python
"""
Test script for the mouse mode functionality.
"""

import sys
import time
from src.mouse_controller import MouseController

def main():
    """Test the mouse controller functionality."""
    print("Testing Mouse Controller for Mortal Online 2")
    print("=" * 50)
    
    # Initialize the mouse controller
    controller = MouseController()
    
    # Test initialization
    print("Initializing mouse controller...")
    if not controller.initialize():
        print("Failed to initialize mouse controller!")
        return 1
    
    print(f"Mouse controller initialized successfully!")
    print(f"Center position: {controller.center_position}")
    
    # Start the controller
    print("Starting mouse controller...")
    controller.start()
    
    try:
        print("\nMouse controller is running!")
        print("Move your mouse around to test the functionality.")
        print("The right mouse button should be pressed when you move outside the deadzone.")
        print("Press Ctrl+C to stop the test.")
        
        # Run for a while and show debug info
        for i in range(100):  # Run for about 10 seconds
            time.sleep(0.1)
            
            # Get debug info every second
            if i % 10 == 0:
                debug_info = controller.get_debug_info()
                print(f"\nDebug Info (iteration {i//10 + 1}):")
                print(f"  Position: {debug_info['position']}")
                print(f"  Relative: {debug_info['relative_position']}")
                print(f"  Angle: {debug_info['angle']:.1f}°")
                print(f"  Distance: {debug_info['distance']:.2f}")
                print(f"  Sector: {debug_info['sector']}")
                print(f"  State: {debug_info['state']}")
                print(f"  Right Mouse: {'PRESSED' if debug_info['right_mouse_pressed'] else 'RELEASED'}")
                print(f"  In Deadzone: {debug_info['in_deadzone']}")
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    
    finally:
        # Stop the controller
        print("Stopping mouse controller...")
        controller.stop()
        print("Mouse controller stopped.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
