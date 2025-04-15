"""
Visualizer module for the Chakram X controller.
Provides visual feedback for the controller state and adaptive control system.
"""

import math
import pygame
from src.config import (
    SECTORS, VISUALIZATION, DEADZONE, DEADZONE_SPEED_THRESHOLD,
    ADAPTIVE_ENABLED, DYNAMIC_DEADZONE_ENABLED, PREDICTION_ENABLED,
    COMBAT_MODE_ENABLED
)

class Visualizer:
    def __init__(self, width=None, height=None):
        """Initialize the visualizer."""
        self.width = width or VISUALIZATION["window_size"][0]
        self.height = height or VISUALIZATION["window_size"][1]
        self.surface = None
        self.font = None
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.radius = min(self.center_x, self.center_y) - 50
    
    def initialize(self):
        """Initialize the pygame surface and font."""
        self.surface = pygame.Surface((self.width, self.height))
        self.font = pygame.font.SysFont(None, 24)
        return self.surface
    
    def draw(self, controller_info):
        """Draw the visualization based on controller information."""
        if not self.surface or not self.font:
            return
            
        # Clear the surface
        self.surface.fill(VISUALIZATION["background_color"])
        
        # Draw the sectors
        self.draw_sectors()
        
        # Draw the thresholds with controller info for dynamic visualization
        self.draw_thresholds(controller_info)
        
        # Draw the joystick position
        self.draw_joystick_position(controller_info["position"])
        
        # Draw the debug information
        self.draw_debug_info(controller_info)
        
        # Draw the pressed keys
        self.draw_pressed_keys(controller_info["pressed_keys"])
        
        # Draw movement trail if available
        if "movement_trail" in controller_info and controller_info["movement_trail"]:
            self.draw_movement_trail(controller_info["movement_trail"])
        
        return self.surface
    
    def draw_sectors(self):
        """Draw the sectors on the surface."""
        for sector_name, sector_range in SECTORS.items():
            start_angle = sector_range["start"]
            end_angle = sector_range["end"]
            color = VISUALIZATION["sector_colors"].get(sector_name, (150, 150, 150))
            
            # Handle sector that wraps around 0°
            if start_angle > end_angle:
                # Draw from start_angle to 360°
                self.draw_sector_arc(start_angle, 360, color)
                # Draw from 0° to end_angle
                self.draw_sector_arc(0, end_angle, color)
            else:
                self.draw_sector_arc(start_angle, end_angle, color)
            
            # Draw sector label
            mid_angle = (start_angle + end_angle) / 2
            if start_angle > end_angle:
                mid_angle = (start_angle + end_angle + 360) / 2
                if mid_angle >= 360:
                    mid_angle -= 360
                    
            label_x = self.center_x + int(self.radius * 0.7 * math.cos(math.radians(mid_angle)))
            label_y = self.center_y + int(self.radius * 0.7 * math.sin(math.radians(mid_angle)))
            
            label = self.font.render(sector_name, True, VISUALIZATION["text_color"])
            label_rect = label.get_rect(center=(label_x, label_y))
            self.surface.blit(label, label_rect)
    
    def draw_sector_arc(self, start_angle, end_angle, color, alpha=40):
        """Draw a sector arc with the given angles and color."""
        # Create a transparent surface for the sector
        sector_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Convert angles to radians (pygame uses radians for arc)
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Draw the arc
        pygame.draw.arc(
            sector_surface,
            (*color, alpha),  # Color with alpha
            (
                self.center_x - self.radius,
                self.center_y - self.radius,
                self.radius * 2,
                self.radius * 2
            ),
            start_rad,
            end_rad,
            width=self.radius
        )
        
        # Blit the transparent surface onto the main surface
        self.surface.blit(sector_surface, (0, 0))
    
    def draw_thresholds(self, controller_info=None):
        """Draw the sector boundaries and deadzone on the surface."""
        # Get the current deadzone from controller info if available
        current_deadzone = controller_info.get("current_deadzone", DEADZONE) if controller_info else DEADZONE
        
        # Draw static deadzone circle (dotted)
        pygame.draw.circle(
            self.surface,
            (80, 80, 80),
            (self.center_x, self.center_y),
            int(self.radius * DEADZONE),
            1
        )
        
        # Draw dynamic deadzone circle if different from static (solid)
        if current_deadzone != DEADZONE:
            pygame.draw.circle(
                self.surface,
                (120, 120, 200),
                (self.center_x, self.center_y),
                int(self.radius * current_deadzone),
                2
            )
        
        # Draw sector boundary lines
        for sector_name, sector_range in SECTORS.items():
            # Draw sector boundary lines
            self.draw_threshold_line(
                sector_range["start"],
                VISUALIZATION["state_colors"]["attack"],
                2
            )
            self.draw_threshold_line(
                sector_range["end"],
                VISUALIZATION["state_colors"]["attack"],
                2
            )
        
        # Draw predicted sector if available
        if controller_info and "predicted_sector" in controller_info and controller_info["predicted_sector"]:
            predicted_sector = controller_info["predicted_sector"]
            prediction_confidence = controller_info.get("prediction_confidence", 0.0)
            
            # Only draw if we have a valid prediction with reasonable confidence
            if predicted_sector in SECTORS and prediction_confidence > 0.2:
                # Draw a pulsing indicator in the predicted sector
                sector_range = SECTORS[predicted_sector]
                mid_angle = (sector_range["start"] + sector_range["end"]) / 2
                if sector_range["start"] > sector_range["end"]:
                    mid_angle = (sector_range["start"] + sector_range["end"] + 360) / 2
                    if mid_angle >= 360:
                        mid_angle -= 360
                
                # Calculate position for prediction indicator
                pred_x = self.center_x + int(self.radius * 0.8 * math.cos(math.radians(mid_angle)))
                pred_y = self.center_y + int(self.radius * 0.8 * math.sin(math.radians(mid_angle)))
                
                # Draw prediction indicator (size based on confidence)
                indicator_size = int(10 + 10 * prediction_confidence)
                indicator_color = (255, 255, 0, int(150 * prediction_confidence))
                
                # Create a transparent surface for the indicator
                indicator_surface = pygame.Surface((indicator_size*2, indicator_size*2), pygame.SRCALPHA)
                pygame.draw.circle(
                    indicator_surface,
                    indicator_color,
                    (indicator_size, indicator_size),
                    indicator_size
                )
                
                # Blit the transparent surface onto the main surface
                self.surface.blit(indicator_surface, (pred_x - indicator_size, pred_y - indicator_size))
    
    def draw_threshold_line(self, angle, color, width=1):
        """Draw a threshold line at the specified angle."""
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Calculate start and end points of the line
        start_x = self.center_x + int(DEADZONE * self.radius * math.cos(angle_rad))
        start_y = self.center_y + int(DEADZONE * self.radius * math.sin(angle_rad))
        
        end_x = self.center_x + int(self.radius * math.cos(angle_rad))
        end_y = self.center_y + int(self.radius * math.sin(angle_rad))
        
        # Draw the line
        pygame.draw.line(
            self.surface,
            color,
            (start_x, start_y),
            (end_x, end_y),
            width
        )
    
    def draw_joystick_position(self, position):
        """Draw the joystick position on the surface."""
        x, y = position
        pos_x = self.center_x + int(x * self.radius)
        pos_y = self.center_y + int(y * self.radius)
        
        # Draw a line from center to joystick position
        pygame.draw.line(
            self.surface,
            (100, 100, 100),
            (self.center_x, self.center_y),
            (pos_x, pos_y),
            1
        )
        
        # Draw the joystick position
        pygame.draw.circle(
            self.surface,
            VISUALIZATION["joystick_color"],
            (pos_x, pos_y),
            8
        )
    
    def draw_debug_info(self, info):
        """Draw debug information on the surface."""
        y = 10
        right_column_x = self.width - 250
        
        # Draw angle and distance
        angle_text = f"Angle: {info['angle']:.1f}°"
        distance_text = f"Distance: {info['distance']:.2f}"
        
        angle_surface = self.font.render(angle_text, True, VISUALIZATION["text_color"])
        distance_surface = self.font.render(distance_text, True, VISUALIZATION["text_color"])
        
        self.surface.blit(angle_surface, (10, y))
        y += 30
        self.surface.blit(distance_surface, (10, y))
        y += 30
        
        # Draw current sector and state
        sector_text = f"Sector: {info['sector'] or 'None'}"
        state_text = f"State: {info['state'] or 'None'}"
        
        sector_surface = self.font.render(sector_text, True, VISUALIZATION["text_color"])
        
        # Use state color for state text
        state_color = VISUALIZATION["state_colors"].get(info["state"], VISUALIZATION["text_color"])
        state_surface = self.font.render(state_text, True, state_color)
        
        self.surface.blit(sector_surface, (10, y))
        y += 30
        self.surface.blit(state_surface, (10, y))
        y += 30
        
        # Draw alternative mode status
        alt_mode_active = info.get('alt_mode_active', False)
        alt_mode_sector = info.get('alt_mode_sector', None)
        
        # Create a prominent indicator for alt mode
        alt_mode_text = f"ALT MODE: {'ACTIVE' if alt_mode_active else 'OFF'}"
        alt_mode_sector_text = f"Alt Mode Sector: {alt_mode_sector or 'None'}"
        
        # Use bright color for alt mode indicator when active
        alt_mode_color = (255, 255, 0) if alt_mode_active else (100, 100, 100)
        alt_mode_surface = self.font.render(alt_mode_text, True, alt_mode_color)
        
        # Draw with a background highlight when active
        if alt_mode_active:
            # Create a background rectangle
            bg_rect = alt_mode_surface.get_rect(topleft=(10, y))
            bg_rect.inflate_ip(10, 4)  # Make it slightly larger
            pygame.draw.rect(self.surface, (50, 50, 0), bg_rect)
            pygame.draw.rect(self.surface, (100, 100, 0), bg_rect, 2)  # Border
        
        self.surface.blit(alt_mode_surface, (10, y))
        y += 30
        
        # Only show alt mode sector if alt mode is active
        if alt_mode_active:
            alt_sector_surface = self.font.render(alt_mode_sector_text, True, VISUALIZATION["text_color"])
            self.surface.blit(alt_sector_surface, (10, y))
            y += 30
        
        # Removed: deadzone speed and thresholds, quick movement indicators
        
        # Draw adaptive control system information in right column
        y_right = 10
        
        # Draw adaptive control system status
        adaptive_enabled = info.get('adaptive_enabled', False)
        adaptive_text = f"Adaptive Control: {'ENABLED' if adaptive_enabled else 'DISABLED'}"
        adaptive_color = (50, 255, 50) if adaptive_enabled else (150, 150, 150)
        adaptive_surface = self.font.render(adaptive_text, True, adaptive_color)
        
        # Draw with a background highlight when active
        if adaptive_enabled:
            bg_rect = adaptive_surface.get_rect(topleft=(right_column_x, y_right))
            bg_rect.inflate_ip(10, 4)
            pygame.draw.rect(self.surface, (0, 50, 0), bg_rect)
            pygame.draw.rect(self.surface, (0, 100, 0), bg_rect, 2)
        
        self.surface.blit(adaptive_surface, (right_column_x, y_right))
        y_right += 30
        
        # Only show adaptive details if enabled
        if adaptive_enabled:
            # Draw combat mode status
            combat_mode_active = info.get('combat_mode_active', False)
            combat_text = f"Combat Mode: {'ACTIVE' if combat_mode_active else 'OFF'}"
            combat_color = (255, 100, 100) if combat_mode_active else (150, 150, 150)
            combat_surface = self.font.render(combat_text, True, combat_color)
            
            # Draw with a background highlight when active
            if combat_mode_active:
                bg_rect = combat_surface.get_rect(topleft=(right_column_x, y_right))
                bg_rect.inflate_ip(10, 4)
                pygame.draw.rect(self.surface, (50, 0, 0), bg_rect)
                pygame.draw.rect(self.surface, (100, 0, 0), bg_rect, 2)
            
            self.surface.blit(combat_surface, (right_column_x, y_right))
            y_right += 30
            
            # Removed: game state information
            # Removed: dynamic deadzone settings
            # Removed: movement speed and transition smoothness details
            
            # Draw prediction info
            if "predicted_sector" in info and info["predicted_sector"]:
                prediction_text = f"Predicted: {info['predicted_sector']}"
                confidence_text = f"Confidence: {info['prediction_confidence']:.2f}"
                
                # Color based on confidence
                confidence = info['prediction_confidence']
                if confidence > 0.7:
                    pred_color = (50, 255, 50)  # Green for high confidence
                elif confidence > 0.4:
                    pred_color = (255, 255, 50)  # Yellow for medium confidence
                else:
                    pred_color = (255, 150, 50)  # Orange for low confidence
                
                pred_surface = self.font.render(prediction_text, True, pred_color)
                conf_surface = self.font.render(confidence_text, True, pred_color)
                
                self.surface.blit(pred_surface, (right_column_x, y_right))
                y_right += 30
                self.surface.blit(conf_surface, (right_column_x, y_right))
                y_right += 30
    
    def draw_pressed_keys(self, pressed_keys):
        """Draw the currently pressed keys on the surface."""
        if not pressed_keys:
            return
            
        y = self.height - 40
        keys_text = f"Pressed keys: {', '.join(pressed_keys)}"
        keys_surface = self.font.render(keys_text, True, VISUALIZATION["text_color"])
        self.surface.blit(keys_surface, (10, y))
    
    def draw_movement_trail(self, trail_points):
        """Draw the movement trail showing recent joystick positions."""
        if not trail_points or len(trail_points) < 2:
            return
        
        # Create a transparent surface for the trail
        trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Convert normalized coordinates to screen coordinates
        screen_points = []
        for x, y in trail_points:
            screen_x = self.center_x + int(x * self.radius)
            screen_y = self.center_y + int(y * self.radius)
            screen_points.append((screen_x, screen_y))
        
        # Draw lines connecting the trail points with fading opacity
        for i in range(1, len(screen_points)):
            # Calculate opacity based on position in trail (newer = more opaque)
            opacity = int(255 * (i / len(screen_points)))
            
            # Draw line segment
            pygame.draw.line(
                trail_surface,
                (100, 200, 255, opacity),  # Blue with variable opacity
                screen_points[i-1],
                screen_points[i],
                2
            )
        
        # Draw small circles at each point
        for i, point in enumerate(screen_points):
            # Calculate size and opacity based on position in trail
            size = 1 + int(3 * (i / len(screen_points)))
            opacity = int(200 * (i / len(screen_points)))
            
            pygame.draw.circle(
                trail_surface,
                (150, 200, 255, opacity),  # Light blue with variable opacity
                point,
                size
            )
        
        # Blit the transparent surface onto the main surface
        self.surface.blit(trail_surface, (0, 0))
