"""
Simple test script to check the interception-python module structure.
"""

try:
    import interception
    print("Successfully imported interception module")
    print("Module attributes:", dir(interception))
    
    # Check if InterceptionContext is available
    if hasattr(interception, 'InterceptionContext'):
        print("InterceptionContext is available")
        try:
            context = interception.InterceptionContext()
            print("Successfully created InterceptionContext instance")
        except Exception as e:
            print(f"Error creating InterceptionContext: {e}")
    else:
        print("InterceptionContext is not available")
        
    # Check for other expected classes
    for class_name in ['InterceptionKeyStroke', 'InterceptionMouseStroke', 'InterceptionKeyState', 'InterceptionMouseState']:
        if hasattr(interception, class_name):
            print(f"{class_name} is available")
        else:
            print(f"{class_name} is not available")
            
except ImportError as e:
    print(f"Error importing interception module: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
