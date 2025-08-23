"""
Main module for the Mouse controller application.
"""

import sys
import pygame
from src.mouse_controller import MouseController
from src.visualizer import Visualizer
from src.config import VISUALIZATION

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

def main():
    """Main function for the Mouse controller application."""
    import os
    
    # Initialize pygame with error handling
    if not initialize_pygame():
        print("Failed to initialize pygame. Cannot continue.")
        return 1
    
    # Check for headless mode
    headless = os.environ.get("CHAKRAM_HEADLESS") == "1"
    
    # Set up the display if not in headless mode
    screen = None
    if not headless:
        try:
            # Try to create the display with additional flags for better compatibility
            screen = pygame.display.set_mode(VISUALIZATION["window_size"], pygame.DOUBLEBUF)
            pygame.display.set_caption("Mouse Controller for Mortal Online 2")
            print(f"Display created successfully: {screen.get_size()}")
            
            # Force an initial display update
            screen.fill((0, 0, 0))
            pygame.display.flip()
            
        except pygame.error as e:
            print(f"Error setting up display: {e}")
            pygame.quit()
            return 1
    
    # Initialize the mouse controller
    controller = MouseController()
    
    # Initialize the controller
    if not controller.initialize():
        print("Failed to initialize mouse controller. Please try again.")
        pygame.quit()
        return 1
    
    # Initialize the visualizer if not in headless mode
    visualizer = None
    if not headless:
        visualizer = Visualizer()
        visualizer.initialize()
    
    # Start the controller background thread
    controller.start_background_thread()
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    try:
        print("Mouse controller is running. Press Ctrl+C or ESC to exit.")
        print("Move your mouse to control the circle. Right mouse button will be pressed when outside deadzone.")
        
        # Debug: Check if we're in headless mode
        if headless:
            print("Running in headless mode - no GUI window")
        else:
            print(f"GUI window created: {VISUALIZATION['window_size']}")
            # Give the window time to fully initialize
            import time
            time.sleep(0.1)
            
            # Clear any pending events that might have accumulated during initialization
            pygame.event.clear()
            print("Window initialization complete, cleared pending events")
        
        frame_count = 0
        last_event_check = 0
        
        while running:
            frame_count += 1
            
            # Debug: Print frame info every 60 frames (once per second at 60 FPS)
            if frame_count % 60 == 0:
                print(f"Frame {frame_count}: Running normally")
            
            # Handle events - but don't process QUIT events too early
            try:
                events = pygame.event.get()
                event_count = len(events)
                
                # Debug: Show event info occasionally
                if event_count > 0 and frame_count % 30 == 0:
                    print(f"Frame {frame_count}: Processing {event_count} events")
                
                for event in events:
                    if event.type == pygame.QUIT:
                        # Only allow QUIT after a few frames to prevent immediate closure
                        if frame_count > 10:
                            print(f"Received QUIT event at frame {frame_count}")
                            running = False
                        else:
                            print(f"Ignoring early QUIT event at frame {frame_count}")
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            print(f"Received ESC key at frame {frame_count}")
                            running = False
                        elif event.key == pygame.K_r:
                            # Reset center position to current mouse position
                            controller.center_position = controller.get_mouse_position()
                            print(f"Center position reset to: {controller.center_position}")
                    elif event.type == pygame.WINDOWCLOSE:
                        print(f"Received WINDOWCLOSE event at frame {frame_count}")
                        if frame_count > 10:
                            running = False
                        else:
                            print(f"Ignoring early WINDOWCLOSE event at frame {frame_count}")
                            
            except Exception as e:
                print(f"Error processing events at frame {frame_count}: {e}")
            
            # Get controller debug info
            controller_info = controller.get_debug_info()
            
            # Draw the visualization if not in headless mode
            if not headless and visualizer and screen:
                # Draw the visualization
                visualization = visualizer.draw(controller_info)
                
                screen.blit(visualization, (0, 0))
                
                # Draw instructions
                font = pygame.font.SysFont(None, 24)
                
                # Mouse mode instructions
                instructions = [
                    "Press ESC to exit",
                    "Move the mouse to control attacks",
                    "Inner circle: Deadzone",
                    "Red lines: Sector boundaries",
                    "Right mouse button is pressed when outside deadzone",
                    "Press R to reset center position to current mouse position",
                    f"Current mode: Mouse",
                    f"Center position: {controller_info.get('center_position', 'Not set')}"
                ]
                
                for i, instruction in enumerate(instructions):
                    text = font.render(instruction, True, VISUALIZATION["text_color"])
                    screen.blit(text, (10, VISUALIZATION["window_size"][1] - 200 + i * 25))
                
                # Update the display
                pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(60)
    except KeyboardInterrupt:
        print("\nController stopped by user.")
    finally:
        # Clean up
        controller.stop_background_thread()
        pygame.quit()
        return 0

if __name__ == "__main__":
    main()
