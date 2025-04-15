"""
Main module for the Chakram X controller application.
"""

import sys
import pygame
from src.chakram_controller import ChakramController
from src.visualizer import Visualizer
from src.trainer import ChakramTrainer
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
    
    # Initialize the trainer
    trainer = None
    if not headless_mode and visualizer:
        trainer = ChakramTrainer(visualizer)
        trainer.initialize()
    
    # Start the controller background thread
    controller.start_background_thread()
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    training_mode = False
    
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
                    # Training mode controls
                    elif event.key == pygame.K_t and trainer:
                        # Toggle regular training mode
                        if not trainer.active:
                            print("Starting regular training exercise...")
                            trainer.start_exercise("random_targets", difficulty=1, duration=60, alt_mode=False)
                        else:
                            print("Stopping training exercise...")
                            trainer.stop_exercise()
                    
                    elif event.key == pygame.K_y and trainer:
                        # Toggle alternative training mode
                        if not trainer.active:
                            print("Starting alternative training exercise (circle targets)...")
                            trainer.start_exercise("circle_targets", difficulty=1, duration=60, alt_mode=True)
                        else:
                            print("Stopping training exercise...")
                            trainer.stop_exercise()
                    elif event.key == pygame.K_1 and trainer:
                        if not trainer.active:
                            # Start easy training
                            trainer.start_exercise("random_targets", difficulty=1, duration=60)
                        else:
                            # Change to difficulty 1 (easy)
                            trainer.difficulty = 1
                            trainer.target_interval = 3.0 - (trainer.difficulty * 0.4)
                            print("Changed to Easy difficulty")
                            
                    elif event.key == pygame.K_2 and trainer:
                        if not trainer.active:
                            # Start medium training
                            trainer.start_exercise("random_targets", difficulty=2, duration=60)
                        else:
                            # Change to difficulty 2
                            trainer.difficulty = 2
                            trainer.target_interval = 3.0 - (trainer.difficulty * 0.4)
                            print("Changed to Medium difficulty")
                            
                    elif event.key == pygame.K_3 and trainer:
                        if not trainer.active:
                            # Start hard training
                            trainer.start_exercise("random_targets", difficulty=3, duration=60)
                        else:
                            # Change to difficulty 3
                            trainer.difficulty = 3
                            trainer.target_interval = 3.0 - (trainer.difficulty * 0.4)
                            print("Changed to Hard difficulty")
                            
                    elif event.key == pygame.K_4 and trainer and trainer.active:
                        # Change to difficulty 4 (expert)
                        trainer.difficulty = 4
                        trainer.target_interval = 3.0 - (trainer.difficulty * 0.4)
                        print("Changed to Expert difficulty")
                        
                    elif event.key == pygame.K_5 and trainer and trainer.active:
                        # Change to difficulty 5 (master)
                        trainer.difficulty = 5
                        trainer.target_interval = 3.0 - (trainer.difficulty * 0.4)
                        print("Changed to Master difficulty")
            
            # Get controller debug info
            controller_info = controller.get_debug_info()
            
            # Update trainer if active
            if trainer and trainer.active:
                trainer.update(controller_info)
            
            # Draw the visualization if not in headless mode
            if not headless_mode and visualizer and screen:
                # Draw the visualization
                visualization = visualizer.draw(controller_info)
                
                # Apply trainer overlay if active
                if trainer and trainer.active:
                    visualization = trainer.draw(visualization)
                
                screen.blit(visualization, (0, 0))
                
                # Draw instructions
                font = pygame.font.SysFont(None, 24)
                
                # Basic instructions
                instructions = [
                    "Press ESC to exit",
                    "Move the joystick to control attacks",
                    "Inner circle: Deadzone",
                    "Red lines: Sector boundaries",
                    "When crossing a sector boundary: Cancel -> Release Old Attack -> Release Cancel -> New Attack",
                    f"Quick movements through deadzone (>{DEADZONE_SPEED_THRESHOLD:.1f}) are ignored",
                    f"Sector change cooldown: {SECTOR_CHANGE_COOLDOWN*1000:.0f}ms to prevent double hits",
                    "Hold ALT for alternative mode: Joystick moves cursor and holds right mouse button"
                ]
                
                # Training mode instructions
                training_instructions = [
                    "--- Training Mode ---",
                    "Press T for sector training mode",
                    "Press Y for precision circle training mode",
                    "Press 1-5 to change difficulty",
                    "1=Easy, 2=Medium, 3=Hard, 4=Expert, 5=Master",
                    "Sector mode: Move to highlighted sectors - targets complete instantly",
                    "Circle mode: Move green cursor inside circle targets - stay within circle"
                ]
                
                # Add training instructions if trainer is available
                if trainer:
                    instructions.extend(training_instructions)
                
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
