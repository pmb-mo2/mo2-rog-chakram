"""
Main module for the Chakram X controller application.
"""

import sys
import pygame
from src.chakram_controller import ChakramController
from src.visualizer import Visualizer
from src.config import VISUALIZATION, DEADZONE_SPEED_THRESHOLD, SECTOR_CHANGE_COOLDOWN

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
    """Main function for the Chakram X controller application."""
    import os
    
    # Initialize pygame with error handling
    if not initialize_pygame():
        print("Failed to initialize pygame. Cannot continue.")
        return 1
    
    # Check for headless mode
    headless_mode = os.environ.get("CHAKRAM_HEADLESS") == "1"
    
    # Get specific joystick ID if provided
    joystick_id = None
    if "CHAKRAM_JOYSTICK_ID" in os.environ:
        try:
            joystick_id = int(os.environ["CHAKRAM_JOYSTICK_ID"])
            print(f"Using specified joystick ID: {joystick_id}")
        except ValueError:
            print(f"Invalid joystick ID in environment: {os.environ['CHAKRAM_JOYSTICK_ID']}")
    
    # Set up the display if not in headless mode
    screen = None
    if not headless_mode:
        try:
            screen = pygame.display.set_mode(VISUALIZATION["window_size"])
            pygame.display.set_caption("Chakram X Controller for Mortal Online 2")
        except pygame.error as e:
            print(f"Error setting up display: {e}")
            pygame.quit()
            return 1
    
    # Initialize the controller
    controller = ChakramController()
    
    # Initialize the controller with automatic or specified joystick detection
    if not controller.initialize(joystick_id):
        print("Failed to initialize a working joystick. Please connect a Chakram X joystick and try again.")
        pygame.quit()
        return 1
    
    # Initialize the visualizer if not in headless mode
    visualizer = None
    if not headless_mode:
        visualizer = Visualizer()
        visualizer.initialize()
    
    # Start the controller background thread
    controller.start_background_thread()
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    try:
        print("Chakram X controller is running. Press Ctrl+C to exit.")
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Get controller debug info
            controller_info = controller.get_debug_info()
            
            # Draw the visualization if not in headless mode
            if not headless_mode and visualizer and screen:
                # Draw the visualization
                visualization = visualizer.draw(controller_info)
                screen.blit(visualization, (0, 0))
                
                # Draw instructions
                font = pygame.font.SysFont(None, 24)
                instructions = [
                    "Press ESC to exit",
                    "Move the joystick to control attacks",
                    "Inner circle: Deadzone",
                    "Red lines: Sector boundaries",
                    "When crossing a sector boundary: Cancel -> Release Old Attack -> Release Cancel -> New Attack",
                    f"Quick movements through deadzone (>{DEADZONE_SPEED_THRESHOLD:.1f}) are ignored",
                    f"Sector change cooldown: {SECTOR_CHANGE_COOLDOWN*1000:.0f}ms to prevent double hits"
                ]
                
                for i, instruction in enumerate(instructions):
                    text = font.render(instruction, True, VISUALIZATION["text_color"])
                    screen.blit(text, (10, VISUALIZATION["window_size"][1] - 150 + i * 25))
                
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
