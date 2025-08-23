"""
Mouse controller module for Mortal Online 2.
Handles mouse input as source of coordinates for the circle with right mouse button attack mode.
"""

import math
import threading
import time
import pygame
from src.win_input import right_mouse_down, right_mouse_up, get_cursor_position, is_right_mouse_pressed, key_down, key_up, send_sector_change
from src.config import (
    SECTORS, KEY_MAPPINGS, DEADZONE, VISUALIZATION
)

class MouseController:
    def __init__(self):
        """Initialize the mouse controller."""
        self.current_sector = None
        self.current_state = None  # "neutral", "attack"
        self.right_mouse_pressed = False
        
        # Thread for background processing
        self.running = False
        self.thread = None
        
        # Position tracking
        self.last_position = (0, 0)
        self.last_position_time = time.time()
        self.center_position = None  # Will be set when mode is activated
        self.in_deadzone = False
        
        # Track the last active sector before entering deadzone
        self.last_active_sector = None
        
        # Track currently pressed attack key
        self.current_attack_key = None
        
        # Debug info
        self.debug_info = {
            "position": (0, 0),
            "relative_position": (0, 0),
            "angle": 0,
            "distance": 0,
            "sector": None,
            "state": None,
            "right_mouse_pressed": False,
            "center_position": None,
            "in_deadzone": False,
            "mode": "mouse"
        }
        
        # Safety mechanism
        self.last_update_time = time.time()
    
    def initialize(self):
        """Initialize the mouse controller."""
        # Get current cursor position as center
        self.center_position = get_cursor_position()
        if self.center_position:
            print(f"Mouse controller initialized. Center position: {self.center_position}")
            return True
        else:
            print("Failed to get cursor position")
            return False
    
    def get_mouse_position(self):
        """Get the current mouse position."""
        return get_cursor_position()
    
    def get_relative_position(self):
        """Get mouse position relative to center."""
        if not self.center_position:
            return (0, 0)
        
        current_pos = self.get_mouse_position()
        if not current_pos:
            return (0, 0)
        
        # Calculate relative position
        rel_x = current_pos[0] - self.center_position[0]
        rel_y = current_pos[1] - self.center_position[1]
        
        return (rel_x, rel_y)
    
    def get_mouse_angle_and_distance(self):
        """
        Convert mouse position to angle (in degrees) and distance from center.
        Returns (angle, distance) tuple.
        """
        rel_x, rel_y = self.get_relative_position()
        
        # Calculate angle (in degrees, 0° is right, 90° is down)
        angle = math.degrees(math.atan2(rel_y, rel_x))
        if angle < 0:
            angle += 360
            
        # Calculate distance from center (in pixels)
        distance = math.sqrt(rel_x*rel_x + rel_y*rel_y)
        
        # Normalize distance to 0.0-1.0 range (assuming 100 pixels = 1.0)
        normalized_distance = min(1.0, distance / 100.0)
        
        return (angle, normalized_distance)
    
    def get_current_sector(self, angle, distance):
        """
        Determine which sector the mouse is currently in based on angle.
        Returns None if the mouse is within the deadzone.
        """
        # In mouse mode, deadzone is zero - no deadzone check needed
        mouse_deadzone = 0.0
        if distance < mouse_deadzone:
            return None
            
        # Standard sector determination
        for sector_name, sector_range in SECTORS.items():
            start = sector_range["start"]
            end = sector_range["end"]
            
            # Handle sector that wraps around 0°
            if start > end:
                if angle >= start or angle <= end:
                    return sector_name
            else:
                if start <= angle <= end:
                    return sector_name
                    
        return None  # Should not happen if sectors cover all 360°
    
    def get_current_state(self, sector, distance):
        """
        Determine the current state based on sector and distance.
        Returns "neutral" or "attack".
        """
        # In mouse mode, deadzone is zero
        mouse_deadzone = 0.0
        if distance < mouse_deadzone:
            return "neutral"
            
        if sector is None:
            return "neutral"
            
        return "attack"
    
    def press_right_mouse(self):
        """Press right mouse button."""
        if not self.right_mouse_pressed:
            try:
                if right_mouse_down():
                    self.right_mouse_pressed = True
                    timestamp = time.time()
                    formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                    ms = int((timestamp - int(timestamp)) * 1000)
                    print(f"[{formatted_time}.{ms:03d}] MOUSE: RIGHT DOWN")
                    return True
                else:
                    print("Failed to press right mouse button")
                    return False
            except Exception as e:
                print(f"Error pressing right mouse button: {e}")
                return False
        return False
    
    def release_right_mouse(self):
        """Release right mouse button."""
        if self.right_mouse_pressed:
            try:
                if right_mouse_up():
                    self.right_mouse_pressed = False
                    timestamp = time.time()
                    formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                    ms = int((timestamp - int(timestamp)) * 1000)
                    print(f"[{formatted_time}.{ms:03d}] MOUSE: RIGHT UP")
                    return True
                else:
                    print("Failed to release right mouse button")
                    return False
            except Exception as e:
                print(f"Error releasing right mouse button: {e}")
                return False
        return False
    
    def check_right_mouse_key(self):
        """Check if right mouse button should be pressed (always true in mouse mode)."""
        # In mouse mode, we use right mouse button as the attack button
        # It should be pressed when we're in attack state
        return True
    
    def update(self):
        """Update the controller state and simulate mouse presses."""
        # Get current time
        current_time = time.time()
        
        # Safety mechanism
        time_since_last_update = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Get mouse position, angle, and distance
        current_position = self.get_mouse_position()
        if not current_position:
            return
        
        relative_position = self.get_relative_position()
        angle, distance = self.get_mouse_angle_and_distance()
        
        # Check real right mouse button state
        real_right_mouse_pressed = is_right_mouse_pressed()
        
        # Only process position and actions when right mouse button is pressed
        if real_right_mouse_pressed:
            # Deadzone detection - in mouse mode, deadzone is zero
            mouse_deadzone = 0.0  # No deadzone in mouse mode
            was_in_deadzone = self.in_deadzone
            self.in_deadzone = distance < mouse_deadzone
            
            # Determine sector and state
            new_sector = self.get_current_sector(angle, distance)
            new_state = "attack" if not self.in_deadzone else "neutral"
        else:
            # When right mouse button is not pressed, stay in neutral state
            # and don't update position/sector
            new_sector = None
            new_state = "neutral"
            self.in_deadzone = True  # Consider as in deadzone when not pressing
            
            # Reset position to center for visualization when not pressing
            relative_position = (0, 0)
            angle = 0
            distance = 0
        
        # Update debug info
        # For visualization, we need to provide normalized position (-1.0 to 1.0)
        # Convert relative pixel position to normalized coordinates
        if self.center_position:
            # Normalize relative position to -1.0 to 1.0 range (assuming 100 pixels = 1.0)
            normalized_x = relative_position[0] / 100.0
            normalized_y = relative_position[1] / 100.0
            # Clamp to reasonable range
            normalized_x = max(-1.0, min(1.0, normalized_x))
            normalized_y = max(-1.0, min(1.0, normalized_y))
            normalized_position = (normalized_x, normalized_y)
        else:
            normalized_position = (0, 0)
        
        self.debug_info["position"] = normalized_position
        self.debug_info["relative_position"] = relative_position
        self.debug_info["angle"] = angle
        self.debug_info["distance"] = distance
        self.debug_info["sector"] = new_sector
        self.debug_info["state"] = new_state
        self.debug_info["right_mouse_pressed"] = real_right_mouse_pressed
        self.debug_info["center_position"] = self.center_position
        self.debug_info["in_deadzone"] = self.in_deadzone
        self.debug_info["mode"] = "mouse"
        self.debug_info["pressed_keys"] = ["right_mouse"] if real_right_mouse_pressed else []
        
        # Handle state changes and attack key management
        if new_state != self.current_state:
            if new_state == "attack" and new_sector:
                # Entering attack state - press attack key for current sector
                attack_key = KEY_MAPPINGS.get(new_sector)
                if attack_key:
                    key_down(attack_key)
                    self.current_attack_key = attack_key
                    print(f"Mouse mode: Entered attack state in sector {new_sector}, pressed {attack_key}")
                else:
                    print(f"Mouse mode: Entered attack state in sector {new_sector}, but no key mapping found")
            elif new_state == "neutral":
                # Entering neutral state - release current attack key
                if self.current_attack_key:
                    key_up(self.current_attack_key)
                    print(f"Mouse mode: Entered neutral state, released {self.current_attack_key}")
                    self.current_attack_key = None
                else:
                    print("Mouse mode: Entered neutral state")
        
        # Handle sector changes within attack state
        elif new_state == "attack" and new_sector != self.current_sector:
            if self.current_sector is not None and new_sector is not None:
                # Sector change - use sector change sequence
                old_attack_key = KEY_MAPPINGS.get(self.current_sector)
                new_attack_key = KEY_MAPPINGS.get(new_sector)
                cancel_key = KEY_MAPPINGS.get("cancel", "middle_mouse")
                
                if old_attack_key and new_attack_key:
                    print(f"Mouse mode: Sector change {self.current_sector} -> {new_sector}")
                    if send_sector_change(cancel_key, old_attack_key, new_attack_key):
                        self.current_attack_key = new_attack_key
                        print(f"Mouse mode: Sector change completed, now pressing {new_attack_key}")
                    else:
                        print("Mouse mode: Sector change failed")
                else:
                    print(f"Mouse mode: Sector change {self.current_sector} -> {new_sector}, but missing key mappings")
        
        self.current_sector = new_sector
        self.current_state = new_state
        
        # Update tracking variables
        self.last_position = current_position
        self.last_position_time = current_time
    
    def start(self):
        """Start the controller."""
        if self.thread is not None and self.thread.is_alive():
            print("Mouse controller is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._background_thread)
        self.thread.daemon = True
        self.thread.start()
        
        print("Mouse controller started")
    
    def stop(self):
        """Stop the controller."""
        self.running = False
        
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        # Release any currently pressed attack key
        if self.current_attack_key:
            key_up(self.current_attack_key)
            print(f"Mouse mode: Released {self.current_attack_key} on stop")
            self.current_attack_key = None
        
        # Release right mouse button when stopping
        self.release_right_mouse()
        
        print("Mouse controller stopped")
    
    def _background_thread(self):
        """Background thread for processing mouse input."""
        print("Mouse controller background thread started")
        
        while self.running:
            # Update controller state
            self.update()
            
            # Sleep to reduce CPU usage
            time.sleep(0.01)  # 10ms sleep for ~100Hz update rate
        
        print("Mouse controller background thread stopped")
    
    def start_background_thread(self):
        """Start the controller background thread. Alias for start()."""
        return self.start()
    
    def stop_background_thread(self):
        """Stop the controller background thread. Alias for stop()."""
        return self.stop()
    
    def get_debug_info(self):
        """Get the current debug info."""
        return self.debug_info
