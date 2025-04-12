"""
Movement analyzer module for the Chakram X controller.
Analyzes joystick movement patterns to enable smart transitions.
"""

import math
import time
from collections import deque

class MovementAnalyzer:
    """
    Analyzes joystick movement patterns to enable smart transitions.
    Tracks position history, calculates velocity and acceleration,
    and predicts future movements.
    """
    
    def __init__(self, history_size=10):
        """
        Initialize the movement analyzer.
        
        Args:
            history_size (int): Number of historical positions to keep
        """
        self.position_history = deque(maxlen=history_size)
        self.velocity_history = deque(maxlen=history_size)
        self.timestamp_history = deque(maxlen=history_size)
        self.history_size = history_size
        
        # Movement metrics
        self.current_velocity = (0, 0)
        self.current_speed = 0
        self.current_acceleration = (0, 0)
        self.current_direction = 0  # in degrees
        
        # Prediction
        self.predicted_position = None
        self.predicted_sector = None
        self.prediction_confidence = 0.0
        
    def update(self, position, timestamp):
        """
        Update the analyzer with a new joystick position.
        
        Args:
            position (tuple): Current joystick position as (x, y)
            timestamp (float): Current timestamp
            
        Returns:
            dict: Movement metrics including velocity, acceleration, etc.
        """
        # Add current position to history
        self.position_history.append(position)
        self.timestamp_history.append(timestamp)
        
        # Calculate velocity if we have at least 2 positions
        if len(self.position_history) >= 2:
            prev_pos = self.position_history[-2]
            prev_time = self.timestamp_history[-2]
            
            # Time difference in seconds
            dt = timestamp - prev_time
            if dt > 0:
                # Calculate velocity (units per second)
                dx = position[0] - prev_pos[0]
                dy = position[1] - prev_pos[1]
                velocity = (dx / dt, dy / dt)
                
                # Add to velocity history
                self.velocity_history.append(velocity)
                
                # Update current velocity
                self.current_velocity = velocity
                
                # Calculate speed (magnitude of velocity)
                self.current_speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
                
                # Calculate direction (in degrees, 0° is right, 90° is down)
                self.current_direction = math.degrees(math.atan2(velocity[1], velocity[0]))
                if self.current_direction < 0:
                    self.current_direction += 360
        
        # Calculate acceleration if we have at least 2 velocities
        if len(self.velocity_history) >= 2:
            prev_vel = self.velocity_history[-2]
            prev_time = self.timestamp_history[-3]  # Corresponding to prev_vel
            
            # Time difference in seconds
            dt = timestamp - prev_time
            if dt > 0:
                # Calculate acceleration (units per second^2)
                dvx = self.current_velocity[0] - prev_vel[0]
                dvy = self.current_velocity[1] - prev_vel[1]
                self.current_acceleration = (dvx / dt, dvy / dt)
        
        # Predict future position and sector
        self._predict_movement()
        
        # Return movement metrics
        return {
            "position": position,
            "velocity": self.current_velocity,
            "speed": self.current_speed,
            "acceleration": self.current_acceleration,
            "direction": self.current_direction,
            "predicted_position": self.predicted_position,
            "predicted_sector": self.predicted_sector,
            "prediction_confidence": self.prediction_confidence
        }
    
    def _predict_movement(self, prediction_time=0.1):
        """
        Predict future joystick position based on current movement.
        
        Args:
            prediction_time (float): Time in the future to predict (seconds)
        """
        if len(self.position_history) < 2 or len(self.velocity_history) < 1:
            self.predicted_position = None
            self.predicted_sector = None
            self.prediction_confidence = 0.0
            return
        
        # Get current position and velocity
        current_pos = self.position_history[-1]
        
        # Simple linear prediction based on velocity
        pred_x = current_pos[0] + self.current_velocity[0] * prediction_time
        pred_y = current_pos[1] + self.current_velocity[1] * prediction_time
        
        # Clamp predicted position to valid joystick range (-1 to 1)
        pred_x = max(-1.0, min(1.0, pred_x))
        pred_y = max(-1.0, min(1.0, pred_y))
        
        self.predicted_position = (pred_x, pred_y)
        
        # Prediction confidence based on consistency of movement
        # Higher speed and consistent direction = higher confidence
        if self.current_speed > 0.5:  # Only predict with significant movement
            self.prediction_confidence = min(1.0, self.current_speed / 2.0)
        else:
            self.prediction_confidence = 0.0
    
    def predict_next_sector(self, sectors, current_sector, deadzone):
        """
        Predict which sector the joystick is moving towards.
        
        Args:
            sectors (dict): Sector definitions
            current_sector (str): Current sector name
            deadzone (float): Deadzone radius
            
        Returns:
            str: Predicted sector name or None if prediction confidence is low
        """
        if self.predicted_position is None or self.prediction_confidence < 0.3:
            return None
        
        # Calculate angle and distance of predicted position
        pred_x, pred_y = self.predicted_position
        angle = math.degrees(math.atan2(pred_y, pred_x))
        if angle < 0:
            angle += 360
            
        distance = math.sqrt(pred_x**2 + pred_y**2)
        
        # Don't predict if within deadzone
        if distance < deadzone:
            return None
            
        # Determine which sector the predicted position is in
        for sector_name, sector_range in sectors.items():
            start = sector_range["start"]
            end = sector_range["end"]
            
            # Handle sector that wraps around 0°
            if start > end:
                if angle >= start or angle <= end:
                    self.predicted_sector = sector_name
                    return sector_name
            else:
                if start <= angle <= end:
                    self.predicted_sector = sector_name
                    return sector_name
                    
        return None
    
    def get_dynamic_deadzone(self, base_deadzone, min_factor=0.8, max_factor=1.5):
        """
        Calculate a dynamic deadzone size based on movement speed.
        
        Args:
            base_deadzone (float): Base deadzone size
            min_factor (float): Minimum multiplier for deadzone
            max_factor (float): Maximum multiplier for deadzone
            
        Returns:
            float: Dynamic deadzone size
        """
        # Faster movements get smaller deadzone for quicker transitions
        # Slower movements get larger deadzone for more stability
        if self.current_speed < 0.5:
            # Slow movement - larger deadzone
            factor = max_factor
        elif self.current_speed > 2.0:
            # Fast movement - smaller deadzone
            factor = min_factor
        else:
            # Linear interpolation between min and max factors
            normalized_speed = (self.current_speed - 0.5) / 1.5
            factor = max_factor - normalized_speed * (max_factor - min_factor)
        
        return base_deadzone * factor
    
    def get_transition_smoothness(self, base_smoothness=0.1, min_factor=0.5, max_factor=2.0):
        """
        Calculate transition smoothness based on movement characteristics.
        
        Args:
            base_smoothness (float): Base smoothness value
            min_factor (float): Minimum multiplier for smoothness
            max_factor (float): Maximum multiplier for smoothness
            
        Returns:
            float: Transition smoothness value
        """
        # Higher speed = smoother transitions (lower value)
        # Lower speed = more precise transitions (higher value)
        if self.current_speed < 0.5:
            # Slow movement - more precise
            factor = max_factor
        elif self.current_speed > 2.0:
            # Fast movement - smoother
            factor = min_factor
        else:
            # Linear interpolation between min and max factors
            normalized_speed = (self.current_speed - 0.5) / 1.5
            factor = max_factor - normalized_speed * (max_factor - min_factor)
        
        return base_smoothness * factor
    
    def is_quick_movement(self, threshold):
        """
        Determine if the current movement is a quick movement.
        
        Args:
            threshold (float): Speed threshold for quick movement
            
        Returns:
            bool: True if current movement is quick, False otherwise
        """
        return self.current_speed > threshold
    
    def get_movement_direction_change(self):
        """
        Calculate how much the movement direction has changed recently.
        
        Returns:
            float: Direction change in degrees (0-180)
        """
        if len(self.position_history) < 3:
            return 0
        
        # Calculate direction from 3 points ago to previous point
        p1 = self.position_history[-3]
        p2 = self.position_history[-2]
        old_dx = p2[0] - p1[0]
        old_dy = p2[1] - p1[1]
        
        if old_dx == 0 and old_dy == 0:
            return 0
        
        old_direction = math.degrees(math.atan2(old_dy, old_dx))
        
        # Calculate current direction
        p3 = self.position_history[-1]
        new_dx = p3[0] - p2[0]
        new_dy = p3[1] - p2[1]
        
        if new_dx == 0 and new_dy == 0:
            return 0
        
        new_direction = math.degrees(math.atan2(new_dy, new_dx))
        
        # Calculate absolute difference in direction
        diff = abs(new_direction - old_direction)
        if diff > 180:
            diff = 360 - diff
            
        return diff
