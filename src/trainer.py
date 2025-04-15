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
        
        # Circle target mode (alternative mode)
        self.use_alt_mode = False
        self.target_circle_center = (0, 0)
        self.target_circle_radius = 30  # Base radius in pixels
        self.cursor_in_circle = False
        self.cursor_position = (0, 0)
        
        # Results display
        self.showing_results = False
        self.results_end_time = 0
        self.results_duration = 5.0  # Show results for 5 seconds
        self.exercise_results = {}
        
        # Exercise settings
        self.difficulty = 1  # 1-5, affects timing and sequence complexity
        self.target_interval = 2.0  # Time between targets (seconds)
        self.exercise_duration = 60  # Exercise duration (seconds)
        self.debug_mode = True  # Print debug messages
    
    def initialize(self):
        """Initialize the trainer resources."""
        self.font = pygame.font.SysFont(None, 32)
        return True
    
    def start_exercise(self, exercise_type="random_targets", difficulty=1, duration=60, alt_mode=False):
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
        
        # Set the mode
        self.use_alt_mode = alt_mode
        
        if self.use_alt_mode:
            # Alt mode with sector targets
            self._generate_alt_target()
            print(f"Exercise started: {exercise_type} (Alt Mode), Difficulty: {difficulty}")
        else:
            # Regular sector mode
            self.target_sector = self._get_random_sector()
            self.total_targets += 1
            print(f"Exercise started: {exercise_type}, Difficulty: {difficulty}")
            print(f"First target: {self.target_sector}")
    
    def stop_exercise(self):
        """Stop the current exercise and return results."""
        accuracy = (self.successful_targets / max(1, self.total_targets)) * 100
        avg_reaction = sum(self.reaction_times) / max(1, len(self.reaction_times))
        
        # Store the results for display
        self.exercise_results = {
            "exercise": self.current_exercise,
            "score": self.score,
            "targets_total": self.total_targets,
            "targets_hit": self.successful_targets,
            "accuracy": accuracy,
            "avg_reaction_time": avg_reaction,
            "duration": time.time() - self.exercise_start_time
        }
        
        # Set up results display timer
        self.showing_results = True
        self.results_end_time = time.time() + self.results_duration
        
        print("Exercise completed!")
        print(f"Score: {self.score}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Average reaction time: {avg_reaction:.2f}s")
        
        # Keep active flag True while showing results, will be set to False when results timeout
        
        return self.exercise_results
    
    def update(self, controller_info):
        """Update the trainer state based on controller information."""
        if not self.active:
            return
            
        current_time = time.time()
        
        # If showing results and the time has expired
        if self.showing_results and current_time > self.results_end_time:
            self.showing_results = False
            self.active = False  # Now actually deactivate after showing results
            self.current_exercise = None
            return
            
        # If just showing results, don't update anything else
        if self.showing_results:
            return
            
        # If no exercise is active and not showing results, just return
        if not self.current_exercise:
            return
        
        # Check if exercise time is up
        if current_time - self.exercise_start_time > self.exercise_duration:
            self.stop_exercise()
            return
            
        # Update cursor position for alt mode
        if self.use_alt_mode:
            # Extract joystick coordinates from controller info
            # These should be normalized values between -1 and 1
            raw_x = controller_info.get("x", 0)
            raw_y = controller_info.get("y", 0)
            
            # Print raw values for debugging
            print(f"DEBUG: Raw joystick values: x={raw_x}, y={raw_y}")
            
            # Convert to screen coordinates
            center_x = self.visualizer.center_x
            center_y = self.visualizer.center_y
            max_radius = self.visualizer.radius * 0.8  # Stay within deadzone circle
            
            # Calculate cursor position (centered in the visualization)
            # Invert y-axis since screen Y increases downward
            cursor_x = center_x + int(raw_x * max_radius)
            cursor_y = center_y - int(raw_y * max_radius)  # Note the negative sign
            self.cursor_position = (cursor_x, cursor_y)
            
            print(f"DEBUG: Cursor position set to: {self.cursor_position}")
            
            # Check if cursor is in sector-shaped target area
            if not self.current_target_completed:
                # Calculate distance from center
                center_x = getattr(self.visualizer, 'center_x', 400)
                center_y = getattr(self.visualizer, 'center_y', 300)
                dx = cursor_x - center_x
                dy = cursor_y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Calculate angle in degrees
                angle_rad = math.atan2(dy, dx)
                angle = math.degrees(angle_rad)
                if angle < 0:
                    angle += 360  # Convert negative angles to 0-360 range
                    
                # Store debug values
                self.debug_cursor_distance = distance
                self.debug_cursor_angle = angle
                
                # Get sector angles
                start_angle = self.target_start_angle
                end_angle = self.target_end_angle
                
                # Print detailed debug info
                print(f"DEBUG: Cursor at ({cursor_x}, {cursor_y}), distance={distance:.1f}px, angle={angle:.1f}°")
                print(f"DEBUG: Target sector: {self.target_sector}, angles: {start_angle}° to {end_angle}°")
                print(f"DEBUG: Target radii: inner={self.target_inner_radius}px, outer={self.target_outer_radius}px")
                
                # Check distance condition
                in_distance_range = (self.target_inner_radius <= distance <= self.target_outer_radius)
                print(f"DEBUG: In distance range: {in_distance_range}")
                
                # Check angle condition
                in_angle_range = False
                if start_angle > end_angle:  # Sector crosses 0°
                    in_angle_range = (angle >= start_angle or angle <= end_angle)
                    print(f"DEBUG: Sector crosses 0° - checking if {angle}° is >= {start_angle}° OR <= {end_angle}°: {in_angle_range}")
                else:
                    in_angle_range = (start_angle <= angle <= end_angle)
                    print(f"DEBUG: Checking if {angle}° is between {start_angle}° and {end_angle}°: {in_angle_range}")
                
                # Determine if cursor is in target sector
                in_sector = in_distance_range and in_angle_range
                print(f"DEBUG: In sector: {in_sector}")
                
                if in_sector:
                    # Target completed!
                    self.current_target_completed = True
                    
                    # Calculate reaction time and update stats
                    reaction_time = current_time - self.last_target_time
                    self.reaction_times.append(reaction_time)
                    self.successful_targets += 1
                    
                    # Calculate score based on reaction time and target size
                    # Smaller targets (shorter sectors) give more points
                    size_factor = 1 + (getattr(self.visualizer, 'radius', 200) - self.target_outer_radius) / 50
                    points = max(1, int((20 - reaction_time * 2) * size_factor))
                    self.score += points
                    
                    print(f"TARGET COMPLETED! Reaction: {reaction_time:.2f}s, Points: {points}, Score: {self.score}")
                    
                    # Generate new target immediately
                    self._generate_alt_target()
                
            # Check if the target has timed out
            # Adjusted to 33% slower as requested (making targets stay 33% longer)
            timeout_time = self.target_interval * 2 / 9 * 1.33  # Approximately 6.8x faster than original
            if not self.current_target_completed and (current_time - self.last_target_time >= timeout_time):
                if self.debug_mode:
                    print(f"Sector target timed out after {current_time - self.last_target_time:.2f}s")
                self._generate_alt_target()
        else:
            # Standard sector mode
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
            # Adjusted to 33% slower as requested (making targets stay 33% longer)
            timeout_time = self.target_interval * 2 / 9 * 1.33  # Approximately 6.8x faster than original
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
    
    def _generate_alt_target(self):
        """Generate a new sector-shaped target within the deadzone."""
        self.last_target_time = time.time()
        
        # Reset the target completion flag
        self.current_target_completed = False
        self.show_success_animation = False
        
        try:
            # Get center of visualization, defaulting to screen center if not available
            center_x = getattr(self.visualizer, 'center_x', 400)
            center_y = getattr(self.visualizer, 'center_y', 300)
            
            # Choose a random sector for the target
            sector_names = list(SECTORS.keys())
            self.target_sector = random.choice(sector_names)
            
            # Get the sector angles
            sector = SECTORS[self.target_sector]
            self.target_start_angle = sector["start"]
            self.target_end_angle = sector["end"]
            
            # Determine target inner and outer radii
            full_radius = getattr(self.visualizer, 'radius', 200)  # Full sector radius
            
            # Calculate inner radius - at least 50px from center as requested
            min_inner_radius = 50  # Minimum distance from center
            
            # Calculate outer radius - smaller than full sector but variable based on difficulty
            # Higher difficulty = smaller target (shorter sector)
            max_outer_radius = full_radius * (0.7 - (self.difficulty * 0.05))  # 70% at easy, down to 45% at hardest
            
            # Set the target radii
            self.target_inner_radius = min_inner_radius
            self.target_outer_radius = max_outer_radius
            
            self.total_targets += 1
            
            print(f"NEW TARGET: sector={self.target_sector}, angles={self.target_start_angle}°-{self.target_end_angle}°, " +
                  f"radius={self.target_inner_radius}-{self.target_outer_radius}px")
        except Exception as e:
            print(f"Error generating sector target: {e}")
            # Set fallback values
            self.target_sector = "N"
            self.target_start_angle = 0
            self.target_end_angle = 45
            self.target_inner_radius = 50
            self.target_outer_radius = 150
    
    def draw(self, surface):
        """Draw the trainer overlay on the visualization surface."""
        if not self.active:
            return surface
        
        # Create a copy of the surface to draw on
        overlay = surface.copy()
        
        # If showing results, draw the results screen
        if self.showing_results:
            self._draw_results_screen(overlay)
            return overlay
            
        # If no active exercise, just return
        if not self.current_exercise:
            return surface
        
        if self.use_alt_mode:
            # Draw alt mode target and cursor
            self._draw_alt_target(overlay)
        else:
            # Draw target sector highlight
            if self.target_sector:
                self._draw_target_sector(overlay, self.target_sector)
        
        # Draw exercise info
        self._draw_exercise_info(overlay)
        
        return overlay
        
    def _draw_results_screen(self, surface):
        """Draw the results screen after exercise completion."""
        # Add a semi-transparent background
        background = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))  # Dark transparent background
        surface.blit(background, (0, 0))
        
        # Get screen center
        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2
        
        # Create a large font for the title
        large_font = pygame.font.SysFont(None, 64)
        medium_font = pygame.font.SysFont(None, 40)
        
        # Draw title
        title_text = large_font.render("EXERCISE COMPLETE!", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(center_x, center_y - 150))
        surface.blit(title_text, title_rect)
        
        # Extract results
        score = self.exercise_results.get("score", 0)
        targets_total = self.exercise_results.get("targets_total", 0)
        targets_hit = self.exercise_results.get("targets_hit", 0)
        accuracy = self.exercise_results.get("accuracy", 0)
        avg_reaction = self.exercise_results.get("avg_reaction_time", 0)
        duration = self.exercise_results.get("duration", 0)
        exercise_type = self.exercise_results.get("exercise", "unknown")
        
        # Format exercise type and mode
        mode_text = "Alt Mode" if self.use_alt_mode else "Standard Mode"
        exercise_display = f"{exercise_type} ({mode_text})"
        
        # Draw results details
        y_pos = center_y - 70
        spacing = 50
        
        # Exercise type
        exercise_text = medium_font.render(f"Exercise: {exercise_display}", True, (200, 200, 255))
        exercise_rect = exercise_text.get_rect(center=(center_x, y_pos))
        surface.blit(exercise_text, exercise_rect)
        
        # Score (large and highlighted)
        y_pos += spacing
        score_text = large_font.render(f"Score: {score}", True, (255, 255, 50))
        score_rect = score_text.get_rect(center=(center_x, y_pos))
        surface.blit(score_text, score_rect)
        
        # Accuracy
        y_pos += spacing
        accuracy_text = medium_font.render(f"Accuracy: {accuracy:.1f}%", True, (50, 255, 50))
        accuracy_rect = accuracy_text.get_rect(center=(center_x, y_pos))
        surface.blit(accuracy_text, accuracy_rect)
        
        # Targets
        y_pos += spacing
        targets_text = medium_font.render(f"Targets: {targets_hit} / {targets_total}", True, (255, 255, 255))
        targets_rect = targets_text.get_rect(center=(center_x, y_pos))
        surface.blit(targets_text, targets_rect)
        
        # Average reaction time
        y_pos += spacing
        reaction_text = medium_font.render(f"Avg Reaction: {avg_reaction:.2f}s", True, (255, 255, 255))
        reaction_rect = reaction_text.get_rect(center=(center_x, y_pos))
        surface.blit(reaction_text, reaction_rect)
        
        # Time countdown
        remaining = max(0, self.results_end_time - time.time())
        countdown_text = medium_font.render(f"Results closing in {remaining:.1f}s", True, (200, 200, 200))
        countdown_rect = countdown_text.get_rect(center=(center_x, center_y + 150))
        surface.blit(countdown_text, countdown_rect)
        
    def _draw_alt_target(self, surface):
        """Draw the sector-shaped target and cursor for the alternative mode."""
        try:
            # Get center and dimensions
            center_x = getattr(self.visualizer, 'center_x', 400)
            center_y = getattr(self.visualizer, 'center_y', 300)
            
            # Pulsing effect
            pulse = (math.sin(time.time() * 5) + 1) / 2  # 0 to 1 pulsing
            alpha = int(100 + 100 * pulse)  # 100-200 alpha
            
            if self.current_target_completed:
                # Target completed - green
                color = (50, 255, 50, alpha)
            else:
                # Normal target - yellow-orange
                color = (255, 200, 50, alpha)
            
            # Create transparent surface for the target
            target_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            
            # Calculate points for the sector shape (inner and outer arcs)
            start_angle_rad = math.radians(self.target_start_angle)
            end_angle_rad = math.radians(self.target_end_angle)
            
            # If end angle is less than start angle, add 360 degrees
            if end_angle_rad < start_angle_rad:
                end_angle_rad += 2 * math.pi
                
            # Number of points to make smooth arcs
            num_points = max(10, int((end_angle_rad - start_angle_rad) * 20 / math.pi))
            
            # Create points for inner and outer arcs
            points = []
            
            # Add outer arc points
            for i in range(num_points + 1):
                angle = start_angle_rad + (end_angle_rad - start_angle_rad) * i / num_points
                x = center_x + int(math.cos(angle) * self.target_outer_radius)
                y = center_y + int(math.sin(angle) * self.target_outer_radius)
                points.append((x, y))
            
            # Add inner arc points in reverse
            for i in range(num_points, -1, -1):
                angle = start_angle_rad + (end_angle_rad - start_angle_rad) * i / num_points
                x = center_x + int(math.cos(angle) * self.target_inner_radius)
                y = center_y + int(math.sin(angle) * self.target_inner_radius)
                points.append((x, y))
            
            # Draw the filled sector
            if len(points) > 2:
                pygame.draw.polygon(target_surface, color, points)
                surface.blit(target_surface, (0, 0))
                
                # Draw the border of the sector
                border_color = (255, 255, 255)
                pygame.draw.lines(surface, border_color, True, points, 2)
            
            # Draw range text
            range_text = self.font.render(f"{self.target_inner_radius}-{self.target_outer_radius}px", True, (255, 255, 255))
            
            # Calculate position for text (middle of the sector)
            mid_angle_rad = (start_angle_rad + end_angle_rad) / 2
            mid_radius = (self.target_inner_radius + self.target_outer_radius) / 2
            text_x = center_x + int(math.cos(mid_angle_rad) * mid_radius)
            text_y = center_y + int(math.sin(mid_angle_rad) * mid_radius)
            
            text_rect = range_text.get_rect(center=(text_x, text_y))
            surface.blit(range_text, text_rect)
            
            # Draw the cursor (green dot)
            cursor_color = (0, 255, 0)
            pygame.draw.circle(surface, cursor_color, self.cursor_position, 5)
            
            # Draw line from center to cursor for reference
            reference_color = (150, 150, 150, 128)
            reference_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            pygame.draw.line(reference_surface, reference_color, (center_x, center_y), self.cursor_position, 1)
            surface.blit(reference_surface, (0, 0))
            
            # Draw debug information
            small_font = pygame.font.SysFont(None, 20)
            debug_y = center_y + 250
            
            # Get debug values
            if hasattr(self, 'debug_cursor_distance') and hasattr(self, 'debug_cursor_angle'):
                # Show distance and angle
                distance_text = small_font.render(f"Distance: {getattr(self, 'debug_cursor_distance', 0):.1f}px", True, (255, 255, 255))
                surface.blit(distance_text, (10, debug_y))
                
                angle_text = small_font.render(f"Angle: {getattr(self, 'debug_cursor_angle', 0):.1f}°", True, (255, 255, 255))
                surface.blit(angle_text, (10, debug_y + 20))
                
                # Show target sector info
                sector_text = small_font.render(f"Target sector: {self.target_sector} ({self.target_start_angle}° to {self.target_end_angle}°)", True, (255, 255, 255))
                surface.blit(sector_text, (10, debug_y + 40))
                
                # Check conditions
                in_distance = self.target_inner_radius <= getattr(self, 'debug_cursor_distance', 0) <= self.target_outer_radius
                
                angle = getattr(self, 'debug_cursor_angle', 0)
                start_angle = self.target_start_angle
                end_angle = self.target_end_angle
                
                in_angle = False
                if start_angle > end_angle:  # Sector crosses 0°
                    in_angle = (angle >= start_angle or angle <= end_angle)
                else:
                    in_angle = (start_angle <= angle <= end_angle)
                
                # Show condition results
                distance_result = small_font.render(f"In distance range: {in_distance}", True, (0, 255, 0) if in_distance else (255, 0, 0))
                surface.blit(distance_result, (10, debug_y + 60))
                
                angle_result = small_font.render(f"In angle range: {in_angle}", True, (0, 255, 0) if in_angle else (255, 0, 0))
                surface.blit(angle_result, (10, debug_y + 80))
                
                in_sector = in_distance and in_angle
                sector_result = small_font.render(f"In target sector: {in_sector}", True, (0, 255, 0) if in_sector else (255, 0, 0))
                surface.blit(sector_result, (10, debug_y + 100))
        except Exception as e:
            print(f"Error drawing sector target: {e}")
            # Draw error message
            error_text = self.font.render("Error drawing target", True, (255, 0, 0))
            surface.blit(error_text, (10, 300))
    
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
