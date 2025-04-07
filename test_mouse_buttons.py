"""
Test script to explore the MouseButton enum in the interception module.
"""

import interception

print("Exploring MouseButton enum:")
try:
    print(f"MouseButton class: {interception.MouseButton}")
    print(f"MouseButton members:")
    for name in dir(interception.MouseButton):
        if not name.startswith('_'):  # Skip private attributes
            value = getattr(interception.MouseButton, name)
            print(f"  - {name}: {value}")
    
    print("\nTesting mouse_down function:")
    print(f"Signature: {interception.mouse_down.__doc__}")
    
    print("\nTesting mouse_up function:")
    print(f"Signature: {interception.mouse_up.__doc__}")
    
    print("\nTesting click function:")
    print(f"Signature: {interception.click.__doc__}")
    
except Exception as e:
    print(f"Error during exploration: {e}")
