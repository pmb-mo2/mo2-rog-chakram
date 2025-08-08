"""
Chakram X controller module for Mortal Online 2.
Handles joystick input and key simulation with adaptive control system.
"""

import math
import threading
import time
import queue
import pygame
from src.win_input import key_down, key_up, send_sector_change, right_mouse_down, right_mouse_up, move_mouse, get_cursor_position
from src.config import (
    SECTORS, KEY_MAPPINGS, DEADZONE, DEADZONE_TIME_THRESHOLD, DEADZONE_SPEED_THRESHOLD,
    RELEASE_DELAY, SECTOR_CHANGE_COOLDOWN, ALT_MODE_KEY, ALT_MODE_CURSOR_OFFSET,
    ADAPTIVE_ENABLED, DYNAMIC_DEADZONE_ENABLED, DYNAMIC_DEADZONE_MIN_FACTOR, DYNAMIC_DEADZONE_MAX_FACTOR,
    PREDICTION_ENABLED, PREDICTION_TIME, PREDICTION_CONFIDENCE_THRESHOLD,
    TRANSITION_SMOOTHNESS, TRANSITION_MIN_FACTOR, TRANSITION_MAX_FACTOR,
    COMBAT_MODE_ENABLED, COMBAT_MODE_KEY, COMBAT_MODE_DEADZONE, COMBAT_MODE_TRANSITION_SMOOTHNESS,
    GAME_STATE_DETECTION_ENABLED, COMBAT_TIMEOUT,
    USE_MOUSE_AXES, MOUSE_AXES_MODIFIERS, MOUSE_AXES_POINTER_LOCK,
    MOUSE_AXES_LOCK_CENTER, MOUSE_AXES_INVERT_Y,
    ATTACK_ON_MODIFIER_RELEASE, AIM_MODIFIER, AIM_REQUIRES_MOVEMENT,
    AIM_DIRECTION_MEMORY_MS, ATTACK_PRESS_DURATION_MS, POST_ATTACK_COOLDOWN_MS,
    BLOCK_WHILE_HELD, BLOCK_KEY
)
from src.movement_analyzer import MovementAnalyzer
from src.game_state_detector import GameStateDetector
from src.mouse_axes import MouseAxes

class ChakramController:
    def __init__(self):
        """Initialize the controller."""
        self.joystick = None
        self.use_mouse_axes = USE_MOUSE_AXES
        self.mouse_axes = (
            MouseAxes(
                MOUSE_AXES_MODIFIERS,
                scale=ALT_MODE_CURSOR_OFFSET,
                pointer_lock=MOUSE_AXES_POINTER_LOCK,
                lock_center=MOUSE_AXES_LOCK_CENTER,
                invert_y=MOUSE_AXES_INVERT_Y,
                attack_on_modifier_release=ATTACK_ON_MODIFIER_RELEASE,
                aim_modifier=AIM_MODIFIER,
                aim_requires_movement=AIM_REQUIRES_MOVEMENT,
                aim_direction_memory_ms=AIM_DIRECTION_MEMORY_MS,
                attack_press_duration_ms=ATTACK_PRESS_DURATION_MS,
                post_attack_cooldown_ms=POST_ATTACK_COOLDOWN_MS,
                block_while_held=BLOCK_WHILE_HELD,
                block_key=BLOCK_KEY,
            )
            if self.use_mouse_axes
            else None
        )
        print(f"use_mouse_axes={self.use_mouse_axes}, modifiers={MOUSE_AXES_MODIFIERS}")
        self.current_sector = None
        self.current_state = None  # "neutral", "cancel", "attack"
        self.pressed_keys = set()
        
        # Thread for background processing
        self.running = False
        self.thread = None
        
        # Key event queue and processing thread
        self.key_event_queue = queue.Queue()
        self.key_event_thread = None
        self.key_event_thread_running = False
        self.sector_change_in_progress = False
        
        # Sector change cooldown to prevent rapid changes
        self.last_sector_change_time = 0
        self.sector_change_cooldown = SECTOR_CHANGE_COOLDOWN
        
        # Position tracking for speed calculation
        self.last_position = (0, 0)
        self.last_position_time = time.time()
        self.in_deadzone = False
        self.deadzone_entry_time = 0
        self.deadzone_entry_position = (0, 0)
        self.deadzone_exit_time = 0
        self.deadzone_exit_position = (0, 0)
        self.deadzone_speed = 0
        
        # Track the last active sector before entering deadzone
        self.last_active_sector = None
        
        # Alternative mode
        self.alt_mode_active = False
        self.alt_mode_key_pressed = False
        self.alt_mode_current_sector = None
        self.alt_mode_right_mouse_down = False
        
        # Adaptive control system
        self.adaptive_enabled = ADAPTIVE_ENABLED
        self.movement_analyzer = MovementAnalyzer(history_size=15)
        self.game_state_detector = GameStateDetector(combat_timeout=COMBAT_TIMEOUT)
        
        # Combat mode
        self.combat_mode_enabled = COMBAT_MODE_ENABLED
        self.combat_mode_active = True  # Force combat mode to be enabled by default
        self.combat_mode_key_pressed = False
        
        # Dynamic deadzone
        self.dynamic_deadzone_enabled = DYNAMIC_DEADZONE_ENABLED
        self.current_deadzone = DEADZONE
        
        # Prediction
        self.prediction_enabled = PREDICTION_ENABLED
        self.predicted_sector = None
        self.prediction_confidence = 0.0
        
        # Debug info
        self.debug_info = {
            "position": (0, 0),
            "angle": 0,
            "distance": 0,
            "sector": None,
            "state": None,
            "pressed_keys": [],
            "deadzone_speed": 0,
            "quick_movement": False,
            "alt_mode_active": False,
            "alt_mode_sector": None,
            "adaptive_enabled": self.adaptive_enabled,
            "combat_mode_active": True,  # Set to True to match the default combat mode state
            "current_deadzone": COMBAT_MODE_DEADZONE,  # Use combat mode deadzone as default
            "predicted_sector": None,
            "prediction_confidence": 0.0,
            "game_state": "exploration",
            "movement_speed": 0.0,
            "transition_smoothness": COMBAT_MODE_TRANSITION_SMOOTHNESS,  # Use combat mode smoothness
            "movement_trail": []  # Store recent positions for trail visualization
        }
        
        # Safety mechanism to prevent infinite loops
        self.last_update_time = time.time()
        self.deadzone_timeout = 0.5  # Timeout in seconds to force exit from deadzone
        self.sector_change_timeout = 0.2  # Timeout for sector change operations
    
    def initialize(self, joystick_id=None):
        """
        Initialize the joystick.
        If joystick_id is None, it will try to find the first working Chakram X joystick.
        """
        if self.use_mouse_axes:
            if self.mouse_axes:
                self.mouse_axes.initialize()
            return True
        if joystick_id is not None:
            # Try to initialize the specified joystick
            try:
                self.joystick = pygame.joystick.Joystick(joystick_id)
                self.joystick.init()
                
                # Check if the joystick has working axes
                if self._check_joystick_axes(self.joystick):
                    print(f"Initialized joystick: {self.joystick.get_name()} (ID: {joystick_id})")
                    return True
                else:
                    print(f"Joystick {joystick_id} does not have working axes")
                    return False
            except pygame.error as e:
                print(f"Error initializing joystick {joystick_id}: {e}")
                return False
        else:
            # Try to find a working Chakram X joystick
            return self._find_working_chakram_joystick()
    
    def _find_working_chakram_joystick(self):
        """Find the first working Chakram X joystick."""
        try:
            joystick_count = pygame.joystick.get_count()
            if joystick_count == 0:
                print("No joysticks found")
                return False
            
            print(f"Searching for working Chakram X joystick among {joystick_count} detected joysticks...")
            chakram_joysticks = []
            
            # First, identify all Chakram X joysticks
            for i in range(joystick_count):
                try:
                    joystick = pygame.joystick.Joystick(i)
                    joystick.init()
                    name = joystick.get_name()
                    
                    if "CHAKRAM" in name.upper():
                        chakram_joysticks.append((i, joystick))
                        print(f"  Found Chakram X joystick: {name} (ID: {i})")
                except pygame.error as e:
                    print(f"  Error initializing joystick {i}: {e}")
            
            if not chakram_joysticks:
                print("No Chakram X joysticks found")
                return False
            
            # Then, check each Chakram X joystick for working axes
            for joystick_id, joystick in chakram_joysticks:
                if self._check_joystick_axes(joystick):
                    self.joystick = joystick
                    print(f"Using Chakram X joystick: {joystick.get_name()} (ID: {joystick_id})")
                    return True
            
            print("No working Chakram X joysticks found")
            return False
        except pygame.error as e:
            print(f"Error finding joysticks: {e}")
            return False
    
    def _check_joystick_axes(self, joystick):
        """Check if the joystick has working axes."""
        try:
            # Check if the joystick has at least 2 axes
            if joystick.get_numaxes() < 2:
                print(f"  Joystick {joystick.get_name()} has insufficient axes: {joystick.get_numaxes()}")
                return False
            
            # Get initial axis values
            initial_values = [joystick.get_axis(i) for i in range(2)]
            
            # Process events to get fresh joystick data
            pygame.event.pump()
            
            # Check if axes respond to input
            current_values = [joystick.get_axis(i) for i in range(2)]
            
            # For testing purposes, we'll consider the joystick working if it has 2 axes
            # In a real application, you might want to check if the axes actually respond to movement
            print(f"  Joystick {joystick.get_name()} has {joystick.get_numaxes()} axes")
            return True
        except pygame.error as e:
            print(f"  Error checking joystick axes: {e}")
            return False
    
    def get_joystick_position(self):
        """Get the current joystick position as (x, y) coordinates."""
        if self.use_mouse_axes and self.mouse_axes:
            return self.mouse_axes.get_axes()
        if not self.joystick:
            return (0, 0)
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)
        return (x, y)
    
    def get_joystick_angle_and_distance(self):
        """
        Convert joystick position to angle (in degrees) and distance from center.
        Returns (angle, distance) tuple.
        """
        x, y = self.get_joystick_position()
        
        # Calculate angle (in degrees, 0° is right, 90° is down)
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
            
        # Calculate distance from center (0.0 to 1.0)
        distance = min(1.0, math.sqrt(x*x + y*y))
        
        return (angle, distance)
    
    def get_current_sector(self, angle, distance):
        """
        Determine which sector the joystick is currently in based on angle.
        Returns None if the joystick is within the deadzone.
        
        With adaptive control system, this uses dynamic deadzone and prediction
        to provide more intuitive control.
        """
        # Get the effective deadzone based on movement patterns and game state
        effective_deadzone = self.get_effective_deadzone()
        
        # Don't determine sector if within deadzone
        if distance < effective_deadzone:
            return None
        
        # If prediction is enabled and we have a predicted sector with high confidence,
        # use it to provide more responsive control
        if (self.adaptive_enabled and self.prediction_enabled and 
            self.predicted_sector and self.prediction_confidence > PREDICTION_CONFIDENCE_THRESHOLD):
            return self.predicted_sector
            
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
    
    def get_effective_deadzone(self):
        """
        Get the effective deadzone size based on movement patterns and game state.
        """
        if not self.adaptive_enabled or not self.dynamic_deadzone_enabled:
            # If adaptive control is disabled, use the static deadzone
            return DEADZONE
        
        # Base deadzone
        base_deadzone = DEADZONE
        
        # If combat mode is active, use the combat deadzone
        if self.combat_mode_active:
            base_deadzone = COMBAT_MODE_DEADZONE
        
        # If game state detection is enabled, adjust based on game state
        if GAME_STATE_DETECTION_ENABLED:
            base_deadzone = self.game_state_detector.get_optimal_deadzone(
                base_deadzone, COMBAT_MODE_DEADZONE)
        
        # If dynamic deadzone is enabled, adjust based on movement speed
        if self.dynamic_deadzone_enabled:
            return self.movement_analyzer.get_dynamic_deadzone(
                base_deadzone, DYNAMIC_DEADZONE_MIN_FACTOR, DYNAMIC_DEADZONE_MAX_FACTOR)
        
        return base_deadzone
    
    def get_transition_smoothness(self):
        """
        Get the transition smoothness based on movement patterns and game state.
        """
        if not self.adaptive_enabled:
            # If adaptive control is disabled, use the static smoothness
            return TRANSITION_SMOOTHNESS
        
        # Base smoothness
        base_smoothness = TRANSITION_SMOOTHNESS
        
        # If combat mode is active, use the combat smoothness
        if self.combat_mode_active:
            base_smoothness = COMBAT_MODE_TRANSITION_SMOOTHNESS
        
        # If game state detection is enabled, adjust based on game state
        if GAME_STATE_DETECTION_ENABLED:
            base_smoothness = self.game_state_detector.get_optimal_transition_smoothness(
                base_smoothness, COMBAT_MODE_TRANSITION_SMOOTHNESS)
        
        # Adjust based on movement speed
        return self.movement_analyzer.get_transition_smoothness(
            base_smoothness, TRANSITION_MIN_FACTOR, TRANSITION_MAX_FACTOR)
    
    def get_current_state(self, sector, angle, distance):
        """
        Determine the current state based on sector and distance.
        Returns "neutral" or "attack".
        """
        if distance < DEADZONE:
            return "neutral"
            
        if sector is None:
            return "neutral"
            
        return "attack"
    
    def _is_angle_in_range(self, angle, start, end):
        """
        Check if an angle is within a range, handling wraparound at 360°.
        """
        # Handle range that wraps around 0°
        if start > end:
            return angle >= start or angle <= end
        else:
            return start <= angle <= end
    
    def press_key(self, key):
        """
        Press a key and add it to the pressed keys set.
        Uses optimized key_down function for maximum speed.
        Supports middle mouse button.
        """
        # Don't press attack keys if in alt mode
        if self.alt_mode_active:
            # Check if this is an attack key (one of the sector keys)
            attack_keys = [KEY_MAPPINGS[sector] for sector in SECTORS.keys()]
            if key in attack_keys:
                print(f"Ignoring attack key press in alt mode: {key}")
                return False
        
        if key not in self.pressed_keys:
            try:
                if key == "middle_mouse":
                    # Import the optimized function for middle mouse down
                    from src.win_input import middle_mouse_down
                    
                    # Send middle mouse down event
                    if middle_mouse_down():
                        self.pressed_keys.add(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] PRESS: {key}")
                        return True
                    else:
                        print(f"Failed to press middle mouse button")
                        return False
                else:
                    # Import the optimized function for key down
                    from src.win_input import key_down
                    
                    # Send key down event
                    if key_down(key):
                        self.pressed_keys.add(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] PRESS: {key}")
                        return True
                    else:
                        print(f"Failed to press key: {key}")
                        return False
            except Exception as e:
                print(f"Error pressing key {key}: {e}")
                return False
        return False
    
    def release_key(self, key):
        """
        Release a key and remove it from the pressed keys set.
        Uses optimized key_up function for maximum speed.
        Supports middle mouse button.
        """
        if key in self.pressed_keys:
            try:
                if key == "middle_mouse":
                    # Import the optimized function for middle mouse up
                    from src.win_input import middle_mouse_up
                    
                    # Send middle mouse up event
                    if middle_mouse_up():
                        self.pressed_keys.remove(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] RELEASE: {key}")
                        return True
                    else:
                        print(f"Failed to release middle mouse button")
                        return False
                else:
                    # Import the optimized function for key up
                    from src.win_input import key_up
                    
                    # Send key up event
                    if key_up(key):
                        self.pressed_keys.remove(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] RELEASE: {key}")
                        return True
                    else:
                        print(f"Failed to release key: {key}")
                        return False
            except Exception as e:
                print(f"Error releasing key {key}: {e}")
                return False
        return False
    
    def release_all_keys(self):
        """Release all pressed keys in a single atomic operation for maximum speed."""
        if not self.pressed_keys:
            return
        
        try:
            # Handle middle mouse button separately
            has_middle_mouse = "middle_mouse" in self.pressed_keys
            regular_keys = [key for key in self.pressed_keys if key != "middle_mouse"]
            
            # Release regular keys
            if regular_keys:
                # Release each key individually
                for key in regular_keys:
                    from src.win_input import key_up
                    key_up(key)
                    self._log_key_action(key, True, batch=True)
            
            # Release middle mouse button if pressed
            if has_middle_mouse:
                from src.win_input import middle_mouse_up
                middle_mouse_up()
                self._log_key_action("middle_mouse", True, batch=True)
            
            # Clear the pressed keys set
            self.pressed_keys.clear()
        except Exception as e:
            print(f"Error releasing all keys: {e}")
            # Fallback to individual key releases if the atomic operation fails
            for key in list(self.pressed_keys):
                self.release_key(key)
            self.pressed_keys.clear()
    
    def _log_key_action(self, key, is_up, batch=False):
        """Log key action with timestamp."""
        timestamp = time.time()
        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
        ms = int((timestamp - int(timestamp)) * 1000)
        action = "RELEASE" if is_up else "PRESS"
        batch_prefix = "BATCH " if batch else ""
        print(f"[{formatted_time}.{ms:03d}] {batch_prefix}{action}: {key}")
    
    def calculate_movement_speed(self, pos1, pos2, time1, time2):
        """Calculate the speed of movement between two positions."""
        if time2 == time1:
            return 0
            
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Calculate distance between positions
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Calculate time difference
        time_diff = time2 - time1
        
        # Calculate speed (distance per second)
        speed = distance / time_diff
        
        return speed
        
        # If in deadzone, release right mouse button and reset sector
        if distance < alt_mode_deadzone:
            if self.alt_mode_right_mouse_down:
                right_mouse_up()
                self.alt_mode_right_mouse_down = False
                # Reduce logging to improve performance
                # print("Alt mode: Released right mouse button (returned to deadzone)")
            
            self.alt_mode_current_sector = None
            return
        
        # If we have a new sector
        if new_sector:
            # If we're changing from one sector to another
            if self.alt_mode_current_sector is not None and new_sector != self.alt_mode_current_sector:
                # Release right mouse button
                if self.alt_mode_right_mouse_down:
                    right_mouse_up()
                    self.alt_mode_right_mouse_down = False
                    # Reduce logging to improve performance
                    # print(f"Alt mode: Released right mouse button (sector change: {self.alt_mode_current_sector} -> {new_sector})")
                
                # Move cursor in the new direction
                self.move_cursor_in_direction(new_sector)
                
                # Press right mouse button again
                right_mouse_down()
                self.alt_mode_right_mouse_down = True
                # Reduce logging to improve performance
                # print(f"Alt mode: Pressed right mouse button (new sector: {new_sector})")
            
            # If we're entering a sector from neutral
            elif self.alt_mode_current_sector is None:
                # Move cursor in the direction
                self.move_cursor_in_direction(new_sector)
                
                # Press right mouse button
                right_mouse_down()
                self.alt_mode_right_mouse_down = True
                # Reduce logging to improve performance
                # print(f"Alt mode: Pressed right mouse button (new sector: {new_sector})")
            
            # Update current sector
            self.alt_mode_current_sector = new_sector
    
    def move_cursor_in_direction(self, sector):
        """Move the cursor in the direction corresponding to the sector."""
        # Get the cursor offset from config
        offset = ALT_MODE_CURSOR_OFFSET
        
        # Use a lookup table for faster direction determination
        # This avoids multiple if-else checks
        direction_map = {
            "right": (offset, 0),
            "left": (-offset, 0),
            "overhead": (0, -offset),
            "thrust": (0, offset)
        }
        
        # Get direction from map or default to (0,0)
        dx, dy = direction_map.get(sector, (0, 0))
        
        if dx == 0 and dy == 0:
            return  # Unknown sector
        
        # Reduce logging to improve performance
        # print(f"Alt mode: Moved cursor by ({dx},{dy})px (sector: {sector})")
        
        # Move the cursor
        move_mouse(dx, dy)
    
    def exit_alt_mode(self):
        """Clean up when exiting alternative mode."""
        # Release right mouse button if it's down
        if self.alt_mode_right_mouse_down:
            right_mouse_up()
            self.alt_mode_right_mouse_down = False
            # Reduce logging to improve performance
            # print("Alt mode: Released right mouse button (exiting alt mode)")
        
        # Reset alt mode state
        self.alt_mode_current_sector = None
    
    def update(self):
        """Update the controller state and simulate key presses."""
        # Get current time
        current_time = time.time()
        
        # Safety mechanism to prevent infinite loops or getting stuck
        time_since_last_update = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Get joystick position, angle, and distance
        current_position = self.get_joystick_position()
        angle, distance = self.get_joystick_angle_and_distance()
        
        # Update movement analyzer with current position and time
        if self.adaptive_enabled:
            movement_metrics = self.movement_analyzer.update(current_position, current_time)
            
            # Update prediction if enabled
            if self.prediction_enabled:
                self.predicted_sector = self.movement_analyzer.predict_next_sector(
                    SECTORS, self.current_sector, self.get_effective_deadzone())
                self.prediction_confidence = movement_metrics["prediction_confidence"]
            
            # Update movement trail for visualization
            # Get the last 10 positions from the movement analyzer
            if hasattr(self.movement_analyzer, 'position_history') and len(self.movement_analyzer.position_history) > 0:
                self.debug_info["movement_trail"] = list(self.movement_analyzer.position_history)
        
        # Check for combat mode toggle with keyboard key
        if self.combat_mode_enabled:
            self.check_combat_mode_toggle()
            
        # Also allow combat mode toggle with joystick button
        try:
            if self.joystick and self.joystick.get_numbuttons() > 1:
                combat_button_pressed = self.joystick.get_button(1)  # Second button
                
                # Toggle combat mode on button press
                if combat_button_pressed and not self.combat_mode_key_pressed:
                    # Button just pressed - toggle combat mode
                    self.combat_mode_active = not self.combat_mode_active
                    self.combat_mode_key_pressed = True
                    print(f"Combat mode {'activated' if self.combat_mode_active else 'deactivated'} (joystick button)")
                elif not combat_button_pressed and self.combat_mode_key_pressed:
                    # Button just released
                    self.combat_mode_key_pressed = False
        except Exception as e:
            print(f"Error checking combat mode button: {e}")
        
        # Check if alt mode key is pressed
        alt_key_pressed = self.check_alt_mode_key()
        
        # Handle alt mode activation/deactivation
        if alt_key_pressed and not self.alt_mode_key_pressed:
            # Alt key just pressed - activate alt mode
            self.alt_mode_active = True
            self.alt_mode_key_pressed = True
            print("Alternative mode activated")
            
            # Release all keys from standard mode
            self.release_all_keys()
            
            # Reset sector change flag to prevent getting stuck
            self.sector_change_in_progress = False
            
        elif not alt_key_pressed and self.alt_mode_key_pressed:
            # Alt key just released - deactivate alt mode
            self.alt_mode_active = False
            self.alt_mode_key_pressed = False
            print("Alternative mode deactivated")
            
            # Clean up alt mode
            self.exit_alt_mode()
            
            # Reset sector change flag to prevent getting stuck
            self.sector_change_in_progress = False
        
        # Get effective deadzone based on movement patterns and game state
        effective_deadzone = self.get_effective_deadzone()
        self.current_deadzone = effective_deadzone
        
        # Simplified deadzone detection - use a direct approach with dynamic deadzone
        was_in_deadzone = self.in_deadzone
        
        # Direct deadzone check with dynamic deadzone
        self.in_deadzone = distance < effective_deadzone
        
        # Calculate movement speed for all frames to get more accurate readings
        movement_speed = self.calculate_movement_speed(
            self.last_position, current_position, 
            self.last_position_time, current_time
        )
        
        # Store the speed for use in deadzone exit logic
        if self.in_deadzone:
            # Update the speed while in deadzone to get the most recent value
            self.deadzone_speed = movement_speed
        
        # Update game state detector if enabled
        if GAME_STATE_DETECTION_ENABLED:
            game_state = self.game_state_detector.update(self.pressed_keys, current_time)
        
        # SIMPLIFIED DEADZONE LOGIC
        # If we just entered the deadzone
        if self.in_deadzone and not was_in_deadzone:
            self.deadzone_entry_time = current_time
            print(f"Entered deadzone at {current_time:.3f}")
            
            # Store the last active sector before entering deadzone
            if self.current_sector is not None:
                self.last_active_sector = self.current_sector
                print(f"Stored last active sector: {self.last_active_sector}")
            
            # Reset sector change flag when entering deadzone
            self.sector_change_in_progress = False
        
        # If we're in the deadzone, check how long we've been there
        if self.in_deadzone:
            deadzone_time = current_time - self.deadzone_entry_time
            
            # If we've been in the deadzone for longer than the threshold, release attack buttons
            if deadzone_time >= DEADZONE_TIME_THRESHOLD and len(self.pressed_keys) > 0:
                print(f"In deadzone for {deadzone_time:.3f}s, releasing all attack keys")
                self.release_all_keys()
                
                # Update state
                self.current_sector = None
                self.current_state = "neutral"
        
        # If we just exited the deadzone
        if not self.in_deadzone and was_in_deadzone:
            print(f"Exited deadzone at {current_time:.3f}")
            
            # Reset sector change flag when exiting deadzone
            self.sector_change_in_progress = False
            
            # Get the new sector after exiting deadzone
            new_sector = self.get_current_sector(angle, distance)
            
            # If we have a valid new sector and a stored last active sector
            # and they are different, trigger a sector change
            if (new_sector is not None and 
                self.last_active_sector is not None and 
                new_sector != self.last_active_sector):
                print(f"Detected sector change through deadzone: {self.last_active_sector} -> {new_sector}")
                
                # Set the sector change flag and update the last change time
                self.sector_change_in_progress = True
                self.last_sector_change_time = current_time
                
                # Handle the sector change directly
                self._enqueue_sector_change(self.last_active_sector, new_sector)
                
                # Update current sector to the new one
                self.current_sector = new_sector
        
        # If alt mode is active, handle it differently
        if self.alt_mode_active:
            # Release any attack keys that might still be pressed
            attack_keys = [KEY_MAPPINGS[sector] for sector in SECTORS.keys()]
            for key in list(self.pressed_keys):
                if key in attack_keys:
                    self.release_key(key)
                    print(f"Released attack key {key} in alt mode")
            
            # Handle alt mode and ensure position is updated in debug info
            self.handle_alt_mode(angle, distance)
            
            # Make sure debug info has the current position
            self.debug_info["position"] = current_position
            self.debug_info["angle"] = angle
            self.debug_info["distance"] = distance
            
            # Update tracking variables for next iteration
            self.last_position = current_position
            self.last_position_time = current_time
            return
        
        # Standard mode processing
        # Determine sector and state - only determine sector if outside deadzone
        new_sector = self.get_current_sector(angle, distance)
        new_state = self.get_current_state(new_sector, angle, distance)
        
        # Determine if this is a quick movement through the deadzone
        quick_movement = False
        if self.adaptive_enabled:
            quick_movement = self.movement_analyzer.is_quick_movement(DEADZONE_SPEED_THRESHOLD)
        else:
            quick_movement = self.deadzone_speed > DEADZONE_SPEED_THRESHOLD
        
        # Update debug info
        self.debug_info["position"] = current_position
        self.debug_info["angle"] = angle
        self.debug_info["distance"] = distance
        self.debug_info["sector"] = new_sector
        self.debug_info["state"] = new_state
        self.debug_info["pressed_keys"] = list(self.pressed_keys)
        self.debug_info["deadzone_speed"] = self.deadzone_speed
        self.debug_info["quick_movement"] = quick_movement
        self.debug_info["alt_mode_active"] = self.alt_mode_active
        self.debug_info["alt_mode_sector"] = self.alt_mode_current_sector
        self.debug_info["adaptive_enabled"] = self.adaptive_enabled
        self.debug_info["combat_mode_active"] = self.combat_mode_active
        self.debug_info["current_deadzone"] = self.current_deadzone
        self.debug_info["predicted_sector"] = self.predicted_sector
        self.debug_info["prediction_confidence"] = self.prediction_confidence
        self.debug_info["game_state"] = self.game_state_detector.current_state if GAME_STATE_DETECTION_ENABLED else "unknown"
        self.debug_info["movement_speed"] = self.movement_analyzer.current_speed if self.adaptive_enabled else movement_speed
        self.debug_info["transition_smoothness"] = self.get_transition_smoothness()
        
        # Skip processing if a sector change is already in progress
        # But add a timeout to prevent getting stuck
        if self.sector_change_in_progress:
            # Check if we've been stuck for too long
            if time_since_last_update > self.sector_change_timeout:
                print(f"Sector change taking too long ({time_since_last_update:.3f}s). Forcing reset.")
                self.sector_change_in_progress = False
                # Continue processing this frame instead of returning
            else:
                # Update tracking variables for next iteration
                self.last_position = current_position
                self.last_position_time = current_time
                return
        
        # Process state changes and button presses
        state_changed = False
        cancel_pressed = False
        
        # Check for cancel button press in any state
        try:
            # Check if joystick has buttons
            if self.joystick and self.joystick.get_numbuttons() > 0:
                # Check the first button (usually the main/cancel button)
                if self.joystick.get_button(0):
                    # Press and release the cancel key
                    cancel_key = KEY_MAPPINGS["cancel"]
                    self.press_key(cancel_key)
                    # Release after a very short delay
                    time.sleep(0.01)  # Reduced from 0.05 to 0.01 for faster response
                    self.release_key(cancel_key)
                    print("Cancel button pressed")
                    cancel_pressed = True
                    
                    # If we're in an attack state, also release the attack key
                    if self.current_state == "attack" and self.current_sector:
                        attack_key = KEY_MAPPINGS[self.current_sector]
                        if attack_key in self.pressed_keys:
                            self.release_key(attack_key)
                            print(f"Released attack key {attack_key} due to cancel button press")
        except Exception as e:
            print(f"Error checking cancel button: {e}")
            
        # Handle sector changes (only if we're not in neutral state and cancel wasn't pressed)
        if not cancel_pressed and new_sector != self.current_sector:
            # When crossing sector boundary:
            if self.current_sector is not None and new_sector is not None:
                # If we've quickly moved through the deadzone, use atomic operation for maximum speed
                if quick_movement and was_in_deadzone:
                    print(f"Quick movement through deadzone detected (speed: {self.deadzone_speed:.2f}). Using atomic operation.")
                    
                    try:
                        # Import the optimized function for sending sector change
                        from src.win_input import send_sector_change
                        
                        cancel_key = KEY_MAPPINGS["cancel"]
                        old_attack_key = KEY_MAPPINGS[self.current_sector]
                        new_attack_key = KEY_MAPPINGS[new_sector]
                        
                        # Use the optimized sector change function that ensures correct key sequence:
                        # 1. Press cancel key
                        # 2. Release old attack key
                        # 3. Release cancel key
                        # 4. Press new attack key
                        send_sector_change(cancel_key, old_attack_key, new_attack_key, 0)
                        
                        # Update the pressed keys set
                        if old_attack_key in self.pressed_keys:
                            self.pressed_keys.remove(old_attack_key)
                            self._log_key_action(old_attack_key, True, batch=True)
                        
                        self.pressed_keys.add(new_attack_key)
                        self._log_key_action(cancel_key, False, batch=True)
                        self._log_key_action(cancel_key, True, batch=True)
                        self._log_key_action(new_attack_key, False, batch=True)
                    except Exception as e:
                        print(f"Error during quick movement handling: {e}")
                        # Fallback to individual key operations if the atomic operation fails
                        if self.current_sector and KEY_MAPPINGS[self.current_sector] in self.pressed_keys:
                            self.release_key(KEY_MAPPINGS[self.current_sector])
                        
                        if new_sector:
                            new_attack_key = KEY_MAPPINGS[new_sector]
                            self.press_key(new_attack_key)
                    
                    # Skip the cooldown period for quick movements
                    self.last_sector_change_time = 0
                else:
                    # Set the sector change flag and update the last change time
                    self.sector_change_in_progress = True
                    self.last_sector_change_time = current_time
                    print(f"Starting sector change: {self.current_sector} -> {new_sector}")
                    # Handle the sector change directly
                    self._enqueue_sector_change(self.current_sector, new_sector)
            elif new_state == "attack" and new_sector:
                # If we're entering a sector from neutral, just press the attack key
                new_attack_key = KEY_MAPPINGS[new_sector]
                self.press_key(new_attack_key)
        
        # Handle state changes within the same sector
        elif new_state != self.current_state:
            if new_state == "attack" and new_sector:
                # If we're entering attack state in the same sector, press the attack key
                new_attack_key = KEY_MAPPINGS[new_sector]
                self.press_key(new_attack_key)
        
        self.current_sector = new_sector
        self.current_state = new_state
        
        # Update tracking variables for next iteration
        self.last_position = current_position
        self.last_position_time = current_time
    
    def check_combat_mode_toggle(self):
        """Check if the combat mode key is pressed and toggle combat mode."""
        try:
            # Import the optimized function for checking key state
            from src.win_input import is_key_pressed
            
            # Check if the combat mode key is pressed
            combat_key_pressed = is_key_pressed(COMBAT_MODE_KEY)
            
            # Toggle combat mode on key press/release
            if combat_key_pressed and not self.combat_mode_key_pressed:
                # Key just pressed - toggle combat mode
                self.combat_mode_active = not self.combat_mode_active
                self.combat_mode_key_pressed = True
                print(f"Combat mode {'activated' if self.combat_mode_active else 'deactivated'}")
            elif not combat_key_pressed and self.combat_mode_key_pressed:
                # Key just released
                self.combat_mode_key_pressed = False
        except Exception as e:
            print(f"Error checking combat mode key: {e}")
    
    def _is_angle_in_range(self, angle, start, end):
        """
        Check if an angle is within a range, handling wraparound at 360°.
        """
        # Handle range that wraps around 0°
        if start > end:
            return angle >= start or angle <= end
        else:
            return start <= angle <= end
    
    def press_key(self, key):
        """
        Press a key and add it to the pressed keys set.
        Uses optimized key_down function for maximum speed.
        Supports middle mouse button.
        """
        # Don't press attack keys if in alt mode
        if self.alt_mode_active:
            # Check if this is an attack key (one of the sector keys)
            attack_keys = [KEY_MAPPINGS[sector] for sector in SECTORS.keys()]
            if key in attack_keys:
                print(f"Ignoring attack key press in alt mode: {key}")
                return False
        
        if key not in self.pressed_keys:
            try:
                if key == "middle_mouse":
                    # Import the optimized function for middle mouse down
                    from src.win_input import middle_mouse_down
                    
                    # Send middle mouse down event
                    if middle_mouse_down():
                        self.pressed_keys.add(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] PRESS: {key}")
                        return True
                    else:
                        print(f"Failed to press middle mouse button")
                        return False
                else:
                    # Import the optimized function for key down
                    from src.win_input import key_down
                    
                    # Send key down event
                    if key_down(key):
                        self.pressed_keys.add(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] PRESS: {key}")
                        return True
                    else:
                        print(f"Failed to press key: {key}")
                        return False
            except Exception as e:
                print(f"Error pressing key {key}: {e}")
                return False
        return False
    
    def release_key(self, key):
        """
        Release a key and remove it from the pressed keys set.
        Uses optimized key_up function for maximum speed.
        Supports middle mouse button.
        """
        if key in self.pressed_keys:
            try:
                if key == "middle_mouse":
                    # Import the optimized function for middle mouse up
                    from src.win_input import middle_mouse_up
                    
                    # Send middle mouse up event
                    if middle_mouse_up():
                        self.pressed_keys.remove(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] RELEASE: {key}")
                        return True
                    else:
                        print(f"Failed to release middle mouse button")
                        return False
                else:
                    # Import the optimized function for key up
                    from src.win_input import key_up
                    
                    # Send key up event
                    if key_up(key):
                        self.pressed_keys.remove(key)
                        # Print trace with timestamp
                        timestamp = time.time()
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ms = int((timestamp - int(timestamp)) * 1000)
                        print(f"[{formatted_time}.{ms:03d}] RELEASE: {key}")
                        return True
                    else:
                        print(f"Failed to release key: {key}")
                        return False
            except Exception as e:
                print(f"Error releasing key {key}: {e}")
                return False
        return False
    
    def release_all_keys(self):
        """Release all pressed keys in a single atomic operation for maximum speed."""
        if not self.pressed_keys:
            return
        
        try:
            # Handle middle mouse button separately
            has_middle_mouse = "middle_mouse" in self.pressed_keys
            regular_keys = [key for key in self.pressed_keys if key != "middle_mouse"]
            
            # Release regular keys
            if regular_keys:
                # Release each key individually
                for key in regular_keys:
                    from src.win_input import key_up
                    key_up(key)
                    self._log_key_action(key, True, batch=True)
            
            # Release middle mouse button if pressed
            if has_middle_mouse:
                from src.win_input import middle_mouse_up
                middle_mouse_up()
                self._log_key_action("middle_mouse", True, batch=True)
            
            # Clear the pressed keys set
            self.pressed_keys.clear()
        except Exception as e:
            print(f"Error releasing all keys: {e}")
            # Fallback to individual key releases if the atomic operation fails
            for key in list(self.pressed_keys):
                self.release_key(key)
            self.pressed_keys.clear()
    
    def _log_key_action(self, key, is_up, batch=False):
        """Log key action with timestamp."""
        timestamp = time.time()
        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
        ms = int((timestamp - int(timestamp)) * 1000)
        action = "RELEASE" if is_up else "PRESS"
        batch_prefix = "BATCH " if batch else ""
        print(f"[{formatted_time}.{ms:03d}] {batch_prefix}{action}: {key}")
    
    def calculate_movement_speed(self, pos1, pos2, time1, time2):
        """Calculate the speed of movement between two positions."""
        if time2 == time1:
            return 0
            
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Calculate distance between positions
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Calculate time difference
        time_diff = time2 - time1
        
        # Calculate speed (distance per second)
        speed = distance / time_diff
        
        return speed
    
    
    def handle_alt_mode(self, angle, distance):
        """Handle the alternative mode functionality."""
        # Determine sector - use a smaller deadzone for more responsiveness in alt mode
        alt_mode_deadzone = DEADZONE * 0.8  # 20% smaller deadzone for alt mode
        
        # Determine sector directly without using get_current_sector to avoid extra calculations
        if distance < alt_mode_deadzone:
            new_sector = None
        else:
            # Direct sector determination for speed
            for sector_name, sector_range in SECTORS.items():
                start = sector_range["start"]
                end = sector_range["end"]
                
                # Handle sector that wraps around 0°
                if start > end:
                    if angle >= start or angle <= end:
                        new_sector = sector_name
                        break
                else:
                    if start <= angle <= end:
                        new_sector = sector_name
                        break
            else:
                new_sector = None
        
        # Get current joystick position for visualization
        current_position = self.get_joystick_position()
        
        # Update debug info with current position and other alt mode info
        self.debug_info["position"] = current_position
        self.debug_info["angle"] = angle
        self.debug_info["distance"] = distance
        self.debug_info["alt_mode_active"] = True
        self.debug_info["alt_mode_sector"] = new_sector
        
        # If in deadzone, release right mouse button and reset sector
        if distance < alt_mode_deadzone:
            if self.alt_mode_right_mouse_down:
                right_mouse_up()
                self.alt_mode_right_mouse_down = False
                # Reduce logging to improve performance
                # print("Alt mode: Released right mouse button (returned to deadzone)")
            
            self.alt_mode_current_sector = None
            return
        
        # If we have a new sector
        if new_sector:
            # If we're changing from one sector to another
            if self.alt_mode_current_sector is not None and new_sector != self.alt_mode_current_sector:
                # Release right mouse button
                if self.alt_mode_right_mouse_down:
                    right_mouse_up()
                    self.alt_mode_right_mouse_down = False
                    # Reduce logging to improve performance
                    # print(f"Alt mode: Released right mouse button (sector change: {self.alt_mode_current_sector} -> {new_sector})")
                
                # Move cursor in the new direction
                self.move_cursor_in_direction(new_sector)
                
                # Press right mouse button again
                right_mouse_down()
                self.alt_mode_right_mouse_down = True
                # Reduce logging to improve performance
                # print(f"Alt mode: Pressed right mouse button (new sector: {new_sector})")
            
            # If we're entering a sector from neutral
            elif self.alt_mode_current_sector is None:
                # Move cursor in the direction
                self.move_cursor_in_direction(new_sector)
                
                # Press right mouse button
                right_mouse_down()
                self.alt_mode_right_mouse_down = True
                # Reduce logging to improve performance
                # print(f"Alt mode: Pressed right mouse button (new sector: {new_sector})")
            
            # Update current sector
            self.alt_mode_current_sector = new_sector
    
    def move_cursor_in_direction(self, sector):
        """Move the cursor in the direction corresponding to the sector."""
        # Get the cursor offset from config
        offset = ALT_MODE_CURSOR_OFFSET
        
        # Use a lookup table for faster direction determination
        # This avoids multiple if-else checks
        direction_map = {
            "right": (offset, 0),
            "left": (-offset, 0),
            "overhead": (0, -offset),
            "thrust": (0, offset)
        }
        
        # Get direction from map or default to (0,0)
        dx, dy = direction_map.get(sector, (0, 0))
        
        if dx == 0 and dy == 0:
            return  # Unknown sector
        
        # Reduce logging to improve performance
        # print(f"Alt mode: Moved cursor by ({dx},{dy})px (sector: {sector})")
        
        # Move the cursor
        move_mouse(dx, dy)
    
    def exit_alt_mode(self):
        """Clean up when exiting alternative mode."""
        # Release right mouse button if it's down
        if self.alt_mode_right_mouse_down:
            right_mouse_up()
            self.alt_mode_right_mouse_down = False
            # Reduce logging to improve performance
            # print("Alt mode: Released right mouse button (exiting alt mode)")
        
        # Reset alt mode state
        self.alt_mode_current_sector = None
    
    def update(self):
        """Update the controller state and simulate key presses."""
        # Get current time
        current_time = time.time()
        
        # Safety mechanism to prevent infinite loops or getting stuck
        time_since_last_update = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Check if alt mode key is pressed
        alt_key_pressed = self.check_alt_mode_key()
        
        # Handle alt mode activation/deactivation
        if alt_key_pressed and not self.alt_mode_key_pressed:
            # Alt key just pressed - activate alt mode
            self.alt_mode_active = True
            self.alt_mode_key_pressed = True
            print("Alternative mode activated")
            
            # Release all keys from standard mode
            self.release_all_keys()
            
            # Reset sector change flag to prevent getting stuck
            self.sector_change_in_progress = False
            
        elif not alt_key_pressed and self.alt_mode_key_pressed:
            # Alt key just released - deactivate alt mode
            self.alt_mode_active = False
            self.alt_mode_key_pressed = False
            print("Alternative mode deactivated")
            
            # Clean up alt mode
            self.exit_alt_mode()
            
            # Reset sector change flag to prevent getting stuck
            self.sector_change_in_progress = False
        
        # Get joystick position, angle, and distance
        current_position = self.get_joystick_position()
        angle, distance = self.get_joystick_angle_and_distance()
        
        # Simplified deadzone detection - use a direct approach
        was_in_deadzone = self.in_deadzone
        
        # Direct deadzone check - no hysteresis or debouncing
        # This makes the deadzone more responsive and predictable
        self.in_deadzone = distance < DEADZONE
        
        # Calculate movement speed for all frames to get more accurate readings
        movement_speed = self.calculate_movement_speed(
            self.last_position, current_position, 
            self.last_position_time, current_time
        )
        
        # Store the speed for use in deadzone exit logic
        if self.in_deadzone:
            # Update the speed while in deadzone to get the most recent value
            self.deadzone_speed = movement_speed
        
        # SIMPLIFIED DEADZONE LOGIC
        # If we just entered the deadzone
        if self.in_deadzone and not was_in_deadzone:
            self.deadzone_entry_time = current_time
            print(f"Entered deadzone at {current_time:.3f}")
            
            # Store the last active sector before entering deadzone
            if self.current_sector is not None:
                self.last_active_sector = self.current_sector
                print(f"Stored last active sector: {self.last_active_sector}")
            
            # Reset sector change flag when entering deadzone
            self.sector_change_in_progress = False
        
        # If we're in the deadzone, check how long we've been there
        if self.in_deadzone:
            deadzone_time = current_time - self.deadzone_entry_time
            
            # If we've been in the deadzone for longer than the threshold, release attack buttons
            if deadzone_time >= DEADZONE_TIME_THRESHOLD and len(self.pressed_keys) > 0:
                print(f"In deadzone for {deadzone_time:.3f}s, releasing all attack keys")
                self.release_all_keys()
                
                # Update state
                self.current_sector = None
                self.current_state = "neutral"
        
        # If we just exited the deadzone
        if not self.in_deadzone and was_in_deadzone:
            print(f"Exited deadzone at {current_time:.3f}")
            
            # Reset sector change flag when exiting deadzone
            self.sector_change_in_progress = False
            
            # Get the new sector after exiting deadzone
            new_sector = self.get_current_sector(angle, distance)
            
            # If we have a valid new sector and a stored last active sector
            # and they are different, trigger a sector change
            if (new_sector is not None and 
                self.last_active_sector is not None and 
                new_sector != self.last_active_sector):
                print(f"Detected sector change through deadzone: {self.last_active_sector} -> {new_sector}")
                
                # Set the sector change flag and update the last change time
                self.sector_change_in_progress = True
                self.last_sector_change_time = current_time
                
                # Handle the sector change directly
                self._enqueue_sector_change(self.last_active_sector, new_sector)
                
                # Update current sector to the new one
                self.current_sector = new_sector
        
        # If alt mode is active, handle it differently
        if self.alt_mode_active:
            self.handle_alt_mode(angle, distance)
            
            # Update tracking variables for next iteration
            self.last_position = current_position
            self.last_position_time = current_time
            return
        
        # Standard mode processing
        # Determine sector and state - only determine sector if outside deadzone
        new_sector = self.get_current_sector(angle, distance)
        new_state = self.get_current_state(new_sector, angle, distance)
        
        # Determine if this is a quick movement through the deadzone
        quick_movement = self.deadzone_speed > DEADZONE_SPEED_THRESHOLD
        
        # Update debug info
        self.debug_info["position"] = current_position
        self.debug_info["angle"] = angle
        self.debug_info["distance"] = distance
        self.debug_info["sector"] = new_sector
        self.debug_info["state"] = new_state
        self.debug_info["pressed_keys"] = list(self.pressed_keys)
        self.debug_info["deadzone_speed"] = self.deadzone_speed
        self.debug_info["quick_movement"] = quick_movement
        self.debug_info["alt_mode_active"] = self.alt_mode_active
        self.debug_info["alt_mode_sector"] = self.alt_mode_current_sector
        
        # Skip processing if a sector change is already in progress
        # But add a timeout to prevent getting stuck
        if self.sector_change_in_progress:
            # Check if we've been stuck for too long
            if time_since_last_update > self.sector_change_timeout:
                print(f"Sector change taking too long ({time_since_last_update:.3f}s). Forcing reset.")
                self.sector_change_in_progress = False
                # Continue processing this frame instead of returning
            else:
                # Update tracking variables for next iteration
                self.last_position = current_position
                self.last_position_time = current_time
                return
        
        # Process state changes and button presses
        state_changed = False
        cancel_pressed = False
        
        # Check for cancel button press in any state
        try:
            # Check if joystick has buttons
            if self.joystick and self.joystick.get_numbuttons() > 0:
                # Check the first button (usually the main/cancel button)
                if self.joystick.get_button(0):
                    # Press and release the cancel key
                    cancel_key = KEY_MAPPINGS["cancel"]
                    self.press_key(cancel_key)
                    # Release after a short delay
                    time.sleep(0.05)
                    self.release_key(cancel_key)
                    print("Cancel button pressed")
                    cancel_pressed = True
                    
                    # If we're in an attack state, also release the attack key
                    if self.current_state == "attack" and self.current_sector:
                        attack_key = KEY_MAPPINGS[self.current_sector]
                        if attack_key in self.pressed_keys:
                            self.release_key(attack_key)
                            print(f"Released attack key {attack_key} due to cancel button press")
        except Exception as e:
            print(f"Error checking cancel button: {e}")
            
        # Handle sector changes (only if we're not in neutral state and cancel wasn't pressed)
        if not cancel_pressed and new_sector != self.current_sector:
            # When crossing sector boundary:
            if self.current_sector is not None and new_sector is not None:
                # If we've quickly moved through the deadzone, use atomic operation for maximum speed
                if quick_movement and was_in_deadzone:
                    print(f"Quick movement through deadzone detected (speed: {self.deadzone_speed:.2f}). Using atomic operation.")
                    
                    try:
                        # Import the optimized function for sending sector change
                        from src.win_input import send_sector_change
                        
                        cancel_key = KEY_MAPPINGS["cancel"]
                        old_attack_key = KEY_MAPPINGS[self.current_sector]
                        new_attack_key = KEY_MAPPINGS[new_sector]
                        
                        # Use the optimized sector change function that ensures correct key sequence:
                        # 1. Press cancel key
                        # 2. Release old attack key
                        # 3. Release cancel key
                        # 4. Press new attack key
                        send_sector_change(cancel_key, old_attack_key, new_attack_key, 0)
                        
                        # Update the pressed keys set
                        if old_attack_key in self.pressed_keys:
                            self.pressed_keys.remove(old_attack_key)
                            self._log_key_action(old_attack_key, True, batch=True)
                        
                        self.pressed_keys.add(new_attack_key)
                        self._log_key_action(cancel_key, False, batch=True)
                        self._log_key_action(cancel_key, True, batch=True)
                        self._log_key_action(new_attack_key, False, batch=True)
                    except Exception as e:
                        print(f"Error during quick movement handling: {e}")
                        # Fallback to individual key operations if the atomic operation fails
                        if self.current_sector and KEY_MAPPINGS[self.current_sector] in self.pressed_keys:
                            self.release_key(KEY_MAPPINGS[self.current_sector])
                        
                        if new_sector:
                            new_attack_key = KEY_MAPPINGS[new_sector]
                            self.press_key(new_attack_key)
                    
                    # Skip the cooldown period for quick movements
                    self.last_sector_change_time = 0
                else:
                    # Set the sector change flag and update the last change time
                    self.sector_change_in_progress = True
                    self.last_sector_change_time = current_time
                    print(f"Starting sector change: {self.current_sector} -> {new_sector}")
                    # Handle the sector change directly
                    self._enqueue_sector_change(self.current_sector, new_sector)
            elif new_state == "attack" and new_sector:
                # If we're entering a sector from neutral, just press the attack key
                new_attack_key = KEY_MAPPINGS[new_sector]
                self.press_key(new_attack_key)
        
        # Handle state changes within the same sector
        elif new_state != self.current_state:
            if new_state == "attack" and new_sector:
                # If we're entering attack state in the same sector, press the attack key
                new_attack_key = KEY_MAPPINGS[new_sector]
                self.press_key(new_attack_key)
        
        self.current_sector = new_sector
        self.current_state = new_state
        
        # Update tracking variables for next iteration
        self.last_position = current_position
        self.last_position_time = current_time
    
    def _enqueue_key_event(self, key, is_up, delay=0):
        """Add a key event to the queue with an optional delay."""
        self.key_event_queue.put((key, is_up, delay))
    
    def _enqueue_sector_change(self, old_sector, new_sector):
        """
        Execute a direct sector change with maximum performance.
        This is a highly optimized version that skips all queuing and directly sends inputs.
        """
        cancel_key = KEY_MAPPINGS["cancel"]
        old_attack_key = KEY_MAPPINGS[old_sector]
        new_attack_key = KEY_MAPPINGS[new_sector]
        
        # First, check if we're still in a valid state to perform the sector change
        # This prevents issues when the joystick has moved back to deadzone during processing
        current_position = self.get_joystick_position()
        angle, distance = self.get_joystick_angle_and_distance()
        
        # If we've moved back to deadzone, cancel the sector change
        if distance < DEADZONE:
            print("Canceling sector change - returned to deadzone")
            self.sector_change_in_progress = False
            
            # Release any pressed keys
            if old_attack_key in self.pressed_keys:
                self.release_key(old_attack_key)
            
            return
        
        try:
            # SIMPLIFIED APPROACH: Use individual key operations for maximum reliability
            # This is more reliable than the atomic operation in some cases
            
            # 1. Press cancel key
            self.press_key(cancel_key)
            
            # 2. Release old attack key
            if old_attack_key in self.pressed_keys:
                self.release_key(old_attack_key)
            
            # 3. Release cancel key (after a very short delay)
            time.sleep(0.01)  # 10ms delay
            self.release_key(cancel_key)
            
            # 4. Press new attack key
            self.press_key(new_attack_key)
            
            # Immediately mark the sector change as complete
            self.sector_change_in_progress = False
            print(f"Sector change completed: {old_sector} -> {new_sector}")
        except Exception as e:
            print(f"Error during sector change: {e}")
            # Reset the sector change flag to prevent getting stuck
            self.sector_change_in_progress = False
            
            # Fallback to individual key operations if the atomic operation fails
            if old_attack_key in self.pressed_keys:
                self.release_key(old_attack_key)
            
            # Only press the new attack key if we're still outside the deadzone
            if distance >= DEADZONE:
                self.press_key(new_attack_key)
    
    def check_alt_mode_key(self):
        """Check if the alt mode key is pressed."""
        try:
            # Import the optimized function for checking key state
            from src.win_input import is_key_pressed
            
            # Check if the alt mode key is pressed
            return is_key_pressed(ALT_MODE_KEY)
        except Exception as e:
            print(f"Error checking alt mode key: {e}")
            return False
    
    def start(self):
        """Start the controller."""
        if self.thread is not None and self.thread.is_alive():
            print("Controller is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._background_thread)
        self.thread.daemon = True
        self.thread.start()
        
        print("Controller started")
    
    def stop(self):
        """Stop the controller."""
        self.running = False
        
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        # Release all keys when stopping
        self.release_all_keys()
        
        # Clean up alt mode if active
        if self.alt_mode_active:
            self.exit_alt_mode()
        
        print("Controller stopped")
    
    def _background_thread(self):
        """Background thread for processing joystick input."""
        print("Background thread started")
        
        while self.running:
            # Process events to get fresh joystick data
            pygame.event.pump()
            
            # Update controller state
            self.update()
            
            # Sleep to reduce CPU usage
            time.sleep(0.01)  # 10ms sleep for ~100Hz update rate
        
        print("Background thread stopped")
    
    def start_background_thread(self):
        """Start the controller background thread. Alias for start()."""
        return self.start()
    
    def stop_background_thread(self):
        """Stop the controller background thread. Alias for stop()."""
        return self.stop()
    
    def get_debug_info(self):
        """Get the current debug info."""
        return self.debug_info
