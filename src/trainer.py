"""
Simple training module for the Chakram X controller.
Provides basic exercises to develop skills with the controller.
"""

import random
import time
import math
import pygame
from src.config import SECTORS, VISUALIZATION, DEADZONE

class ChakramTrainer:
    def __init__(self, visualizer):
        """Initialize the trainer with a reference to the visualizer."""
        self.visualizer = visualizer
        self.active = False
        self.current_exercise = None
        self.exercise_start_time = 0
        self.target_sector = None
        self.score = 0
        self.total_targets = 0
        self.successful_targets = 0
        self.reaction_times = []
        self.font = None
        
        # Target tracking
        self.last_target_time = 0
        self.sector_entry_time = 0   # Time when user entered the target sector
        self.in_target_sector = False
        self.current_target_completed = False
        self.target_completed_time = 0  # Time when the current target was completed
        self.show_success_animation = False
        
        # Exercise settings
        self.difficulty = 1  # 1-5, affects timing and sequence complexity
        self.target_interval = 2.0  # Time between targets (seconds)
        self.exercise_duration = 60  # Exercise duration (seconds)
        self.debug_mode = True  # Print debug messages
    
    def initialize(self):
        """Initialize the trainer resources."""
        self.font = pygame.font.SysFont(None, 32)
        return True
    
    def start_exercise(self, exercise_type="random_targets", difficulty=1, duration=60):
        """Start a training exercise."""
        self.active = True
        self.current_exercise = exercise_type
        self.exercise_start_time = time.time()
        self.score = 0
        self.total_targets = 0
        self.successful_targets = 0
        self.reaction_times = []
        self.difficulty = max(1, min(5, difficulty))  # Clamp between 1-5
        self.exercise_duration = duration
        self.target_interval = 3.0 - (self.difficulty * 0.4)  # 3.0s to 1.0s based on difficulty
        self.last_target_time = time.time()
        self.target_sector = self._get_random_sector()
        self.total_targets += 1
        print(f"Exercise started: {exercise_type}, Difficulty: {difficulty}")
        print(f"First target: {self.target_sector}")
    
    def stop_exercise(self):
        """Stop the current exercise and return results."""
        self.active = False
        accuracy = (self.successful_targets / max(1, self.total_targets)) * 100
        avg_reaction = sum(self.reaction_times) / max(1, len(self.reaction_times))
        
        results = {
            "exercise": self.current_exercise,
            "score": self.score,
            "targets_total": self.total_targets,
            "targets_hit": self.successful_targets,
            "accuracy": accuracy,
            "avg_reaction_time": avg_reaction,
            "duration": time.time() - self.exercise_start_time
        }
        
        self.current_exercise = None
        print("Exercise completed!")
        print(f"Score: {self.score}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Average reaction time: {avg_reaction:.2f}s")
        
        return results
    
    def update(self, controller_info):
        """Update the trainer state based on controller information."""
        if not self.active or not self.current_exercise:
            return
        
        current_time = time.time()
        
        # Check if exercise time is up
        if current_time - self.exercise_start_time > self.exercise_duration:
            self.stop_exercise()
            return
        
        # Get current sector from controller info
        current_sector = controller_info.get("sector")
        
        # If user is in the target sector and we haven't completed it yet
        if current_sector == self.target_sector and not self.current_target_completed:
            # Target completed immediately upon entry!
            
            # Calculate reaction time and update stats
            reaction_time = current_time - self.last_target_time
            self.reaction_times.append(reaction_time)
            self.successful_targets += 1
            
            # Calculate score based on reaction time (faster = more points)
            points = max(1, int(20 - reaction_time * 2))
            self.score += points
            
            if self.debug_mode:
                print(f"TARGET COMPLETED! Reaction: {reaction_time:.2f}s, Points: {points}, Score: {self.score}")
            
            # Generate new target immediately
            self._generate_new_target()
        
        # Check if target has timed out (taking too long without completion)
        timeout_time = self.target_interval * 2
        if not self.current_target_completed and (current_time - self.last_target_time >= timeout_time):
            if self.debug_mode:
                print(f"Target timed out after {current_time - self.last_target_time:.2f}s")
            self._generate_new_target()
    
    def _is_target_completed(self):
        """Check if the current target has been completed."""
        # Track if this target has been completed
        if not hasattr(self, 'current_target_completed'):
            self.current_target_completed = False
        return self.current_target_completed
    
    def _generate_new_target(self):
        """Generate a new target sector."""
        self.last_target_time = time.time()
        
        # Reset the target completion flag
        self.current_target_completed = False
        
        # Choose a different sector than the current one
        new_sector = self._get_random_sector()
        while new_sector == self.target_sector:
            new_sector = self._get_random_sector()
        
        self.target_sector = new_sector
        self.total_targets += 1
        print(f"New target: {self.target_sector}")
    
    def _get_random_sector(self):
        """Get a random sector from the available sectors."""
        return random.choice(list(SECTORS.keys()))
    
    def draw(self, surface):
        """Draw the trainer overlay on the visualization surface."""
        if not self.active or not self.current_exercise:
            return surface
        
        # Create a copy of the surface to draw on
        overlay = surface.copy()
        
        # Draw target sector highlight
        if self.target_sector:
            self._draw_target_sector(overlay, self.target_sector)
        
        # Draw exercise info
        self._draw_exercise_info(overlay)
        
        return overlay
    
    def _draw_target_sector(self, surface, sector_name):
        """Draw a highlight for the target sector."""
        if sector_name not in SECTORS:
            return
        
        # Get sector angles
        sector = SECTORS[sector_name]
        start_angle = sector["start"]
        end_angle = sector["end"]
        
        # Get center and radius from visualizer
        center_x = self.visualizer.center_x
        center_y = self.visualizer.center_y
        radius = self.visualizer.radius
        
        # Determine if this target is completed
        target_completed = self.current_target_completed
        
        # Determine the visual style based on completion state
        if target_completed:
            # Success highlight - bright green pulsing
            pulse = (math.sin(time.time() * 10) + 1) / 2  # Faster pulsing for success
            alpha = int(150 + 100 * pulse)  # 150-250 alpha
            highlight_color = (50, 255, 50)  # Bright green for success
        else:
            # Normal target highlight - color based on sector with pulsing
            pulse = (math.sin(time.time() * 5) + 1) / 2  # Normal pulsing
            alpha = int(100 + 100 * pulse)  # 100-200 alpha
            
            # Get sector color with increased brightness
            base_color = VISUALIZATION["sector_colors"].get(sector_name, (150, 150, 150))
            highlight_color = tuple(min(255, c + 50) for c in base_color)
        
        # Draw the arc with alpha
        self.visualizer.draw_sector_arc(start_angle, end_angle, highlight_color, alpha)
        
        # Determine center of sector for text
        mid_angle = (start_angle + end_angle) / 2
        if start_angle > end_angle:
            mid_angle = (start_angle + end_angle + 360) / 2
            if mid_angle >= 360:
                mid_angle -= 360
                
        text_x = center_x + int(radius * 0.7 * math.cos(math.radians(mid_angle)))
        text_y = center_y + int(radius * 0.7 * math.sin(math.radians(mid_angle)))
        
        # Draw sector text
        if target_completed:
            # Success text
            success_text = self.font.render("SUCCESS!", True, (50, 255, 50))
            text_rect = success_text.get_rect(center=(text_x, text_y))
            surface.blit(success_text, text_rect)
            
            # Display points earned
            points_text = self.font.render(f"+{int(20 - (self.sector_entry_time - self.last_target_time) * 2)} pts", True, (255, 255, 50))
            points_rect = points_text.get_rect(center=(text_x, text_y + 30))
            surface.blit(points_text, points_rect)
        else:
            # Normal target text
            target_text = self.font.render("TARGET", True, (255, 255, 255))
            text_rect = target_text.get_rect(center=(text_x, text_y))
            surface.blit(target_text, text_rect)
    
    def _draw_exercise_info(self, surface):
        """Draw exercise information on the surface."""
        # Draw exercise name and difficulty
        difficulty_name = ["Easy", "Medium", "Hard", "Expert", "Master"][min(self.difficulty-1, 4)]
        exercise_text = self.font.render(f"Exercise: {self.current_exercise} ({difficulty_name})", True, (255, 255, 255))
        surface.blit(exercise_text, (10, 10))
        
        # Draw difficulty indicator
        diff_text = self.font.render(f"Difficulty: {self.difficulty}/5", True, (255, 255, 255))
        surface.blit(diff_text, (10, 50))
        
        # Draw keyboard controls
        controls_text = self.font.render("Press 1-5 to change difficulty", True, (200, 200, 255))
        surface.blit(controls_text, (10, 90))
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (10, 130))
        
        # Draw accuracy
        accuracy = (self.successful_targets / max(1, self.total_targets)) * 100
        accuracy_text = self.font.render(f"Accuracy: {accuracy:.1f}%", True, (255, 255, 255))
        surface.blit(accuracy_text, (10, 170))
        
        # Draw time remaining
        remaining = max(0, self.exercise_duration - (time.time() - self.exercise_start_time))
        time_text = self.font.render(f"Time: {int(remaining)}s", True, (255, 255, 255))
        surface.blit(time_text, (10, 210))
