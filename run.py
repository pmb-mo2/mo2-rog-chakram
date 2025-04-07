#!/usr/bin/env python
"""
Launcher script for the Chakram X Alternative Control System for Mortal Online 2.
"""

import os
import sys
import subprocess
import importlib.util

# Set environment variable for background joystick events
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

def main():
    """Main function to run the Chakram X controller."""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Launcher for Chakram X Alternative Control System")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no GUI)")
    parser.add_argument("--joystick", type=int, help="Specific joystick ID to use")
    parser.add_argument("--config", action="store_true", help="Launch the configuration editor")
    parser.add_argument("--check", action="store_true", help="Run joystick check utility")
    args = parser.parse_args()
    
    # Check if we should launch the config editor
    if args.config:
        try:
            from src.config_editor_tk import run_config_editor
            print("Launching Chakram X Controller Configuration Editor...")
            run_config_editor()
            return 0
        except Exception as e:
            print(f"Error launching configuration editor: {e}")
            return 1
    
    # Check if we should run the joystick check utility
    elif args.check:
        try:
            # Import and run the check.py module
            spec = importlib.util.spec_from_file_location("check", "check.py")
            check_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(check_module)
            
            print("Running Chakram X joystick check utility...")
            return check_module.main()
        except Exception as e:
            print(f"Error running joystick check utility: {e}")
            return 1
    
    else:
        # Run the main application
        try:
            # Import the main module
            from src.main import main as run_main
            
            # Set joystick ID in environment if specified
            if args.joystick is not None:
                os.environ["CHAKRAM_JOYSTICK_ID"] = str(args.joystick)
            
            # Set headless mode in environment if specified
            if args.headless:
                os.environ["CHAKRAM_HEADLESS"] = "1"
                print("Running in headless mode (no GUI)")
            
            print("Starting Chakram X Alternative Control System for Mortal Online 2...")
            return run_main()
        except KeyboardInterrupt:
            print("\nApplication terminated by user.")
            return 0
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
