#!/usr/bin/env python
"""
Test script for pygame joystick input.
This script displays the joystick input values in real-time.
"""

import sys
import math
import pygame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

class JoystickTester:
    """Class for testing joystick input."""
    
    def __init__(self):
        """Initialize the joystick tester."""
        self.screen = None
        self.clock = None
        self.font = None
        self.joystick = None
        self.running = False
    
    def initialize(self, width=800, height=600):
        """Initialize pygame and the joystick."""
        pygame.init()
        pygame.display.set_caption("Pygame Joystick Tester")
        
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        # Initialize joystick
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Initialized joystick: {self.joystick.get_name()}")
            return True
        else:
            print("No joysticks found. Please connect a joystick and try again.")
            return False
    
    def draw_text(self, text, position, color=WHITE):
        """Draw text on the screen."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)
    
    def draw_joystick_position(self, x, y, center_x, center_y, radius):
        """Draw the joystick position."""
        # Draw the joystick area
        pygame.draw.circle(self.screen, GRAY, (center_x, center_y), radius, 1)
        
        # Draw the center point
        pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 5)
        
        # Draw the joystick position
        pos_x = center_x + int(x * radius)
        pos_y = center_y + int(y * radius)
        
        # Draw a line from center to joystick position
        pygame.draw.line(self.screen, WHITE, (center_x, center_y), (pos_x, pos_y), 1)
        
        # Draw the joystick position
        pygame.draw.circle(self.screen, GREEN, (pos_x, pos_y), 10)
        
        # Calculate angle and distance
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
        
        distance = min(1.0, math.sqrt(x*x + y*y))
        
        # Draw angle and distance
        self.draw_text(f"Angle: {angle:.1f}°", (center_x - 50, center_y + radius + 20))
        self.draw_text(f"Distance: {distance:.2f}", (center_x - 50, center_y + radius + 50))
    
    def draw_axes(self):
        """Draw all joystick axes."""
        if not self.joystick:
            return
        
        # Get screen dimensions
        width, height = self.screen.get_size()
        
        # Draw the main joystick position (first two axes)
        center_x = width // 4
        center_y = height // 3
        radius = min(center_x, center_y) - 50
        
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)
        
        self.draw_text("Joystick Position (Axes 0, 1)", (center_x - 100, center_y - radius - 30))
        self.draw_joystick_position(x, y, center_x, center_y, radius)
        
        # Draw all axes as bars
        num_axes = self.joystick.get_numaxes()
        bar_width = width - 100
        bar_height = 20
        bar_spacing = 30
        
        self.draw_text("All Axes", (50, height // 2))
        
        for i in range(num_axes):
            value = self.joystick.get_axis(i)
            
            # Draw axis label
            self.draw_text(f"Axis {i}", (50, height // 2 + 30 + i * bar_spacing))
            
            # Draw axis bar background
            pygame.draw.rect(self.screen, GRAY, (100, height // 2 + 30 + i * bar_spacing, bar_width, bar_height))
            
            # Draw axis bar value
            bar_value = int((value + 1) / 2 * bar_width)
            pygame.draw.rect(self.screen, BLUE, (100, height // 2 + 30 + i * bar_spacing, bar_value, bar_height))
            
            # Draw axis value
            self.draw_text(f"{value:.2f}", (100 + bar_width + 10, height // 2 + 30 + i * bar_spacing))
    
    def draw_buttons(self):
        """Draw all joystick buttons."""
        if not self.joystick:
            return
        
        # Get screen dimensions
        width, height = self.screen.get_size()
        
        # Draw all buttons
        num_buttons = self.joystick.get_numbuttons()
        button_size = 30
        button_spacing = 40
        buttons_per_row = 8
        
        self.draw_text("Buttons", (width // 2, height // 2))
        
        for i in range(num_buttons):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            x = width // 2 + col * button_spacing
            y = height // 2 + 30 + row * button_spacing
            
            # Draw button background
            pygame.draw.rect(self.screen, GRAY, (x, y, button_size, button_size))
            
            # Draw button state
            if self.joystick.get_button(i):
                pygame.draw.rect(self.screen, RED, (x, y, button_size, button_size))
            
            # Draw button label
            self.draw_text(str(i), (x + 10, y + 5))
    
    def run(self):
        """Run the joystick tester."""
        self.running = True
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Clear the screen
            self.screen.fill(BLACK)
            
            # Draw joystick information
            if self.joystick:
                self.draw_text(f"Joystick: {self.joystick.get_name()}", (10, 10))
                self.draw_text(f"Axes: {self.joystick.get_numaxes()}", (10, 40))
                self.draw_text(f"Buttons: {self.joystick.get_numbuttons()}", (10, 70))
                self.draw_text(f"Hats: {self.joystick.get_numhats()}", (10, 100))
                
                self.draw_axes()
                self.draw_buttons()
            else:
                self.draw_text("No joystick connected", (10, 10))
            
            # Draw instructions
            self.draw_text("Press ESC to exit", (10, self.screen.get_height() - 30))
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
    
    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()

def main():
    """Main function."""
    tester = JoystickTester()
    
    if not tester.initialize():
        pygame.quit()
        return 1
    
    try:
        tester.run()
    finally:
        tester.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
