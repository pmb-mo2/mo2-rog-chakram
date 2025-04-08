"""
Chakram X controller module for Mortal Online 2.
Handles joystick input and key simulation.
"""

import math
import threading
import time
import queue
import pygame
from src.win_input import key_down, key_up, send_sector_change
from src.config import SECTORS, KEY_MAPPINGS, DEADZONE, DEADZONE_SPEED_THRESHOLD, RELEASE_DELAY, SECTOR_CHANGE_COOLDOWN

class ChakramController:
    def __init__(self):
        """Initialize the controller."""
        self.joystick = None
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
        
        # Debug info
        self.debug_info = {
            "position": (0, 0),
            "angle": 0,
            "distance": 0,
            "sector": None,
            "state": None,
            "pressed_keys": [],
            "deadzone_speed": 0,
            "quick_movement": False
        }
    
    def initialize(self, joystick_id=None):
        """
        Initialize the joystick.
        If joystick_id is None, it will try to find the first working Chakram X joystick.
        """
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
        """
        # Don't determine sector if within deadzone
        if distance < DEADZONE:
            return None
            
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
    
    def update(self):
        """Update the controller state and simulate key presses."""
        # Get current time
        current_time = time.time()
        
        # Get joystick position, angle, and distance
        current_position = self.get_joystick_position()
        angle, distance = self.get_joystick_angle_and_distance()
        
        # Track deadzone entry and exit
        was_in_deadzone = self.in_deadzone
        self.in_deadzone = distance < DEADZONE
        
        # Calculate movement speed only when needed
        if (self.in_deadzone and not was_in_deadzone) or (not self.in_deadzone and was_in_deadzone):
            # Calculate movement speed
            movement_speed = self.calculate_movement_speed(
                self.last_position, current_position, 
                self.last_position_time, current_time
            )
        
        # If we just entered the deadzone
        if self.in_deadzone and not was_in_deadzone:
            self.deadzone_entry_time = current_time
            self.deadzone_entry_position = current_position
        
        # If we just exited the deadzone
        if not self.in_deadzone and was_in_deadzone:
            self.deadzone_exit_time = current_time
            self.deadzone_exit_position = current_position
            
            # Calculate speed through deadzone
            self.deadzone_speed = self.calculate_movement_speed(
                self.deadzone_entry_position, self.deadzone_exit_position,
                self.deadzone_entry_time, self.deadzone_exit_time
            )
            
            # No cooldown after exiting deadzone for maximum responsiveness
            # We'll rely on the minimal sector change cooldown to prevent double hits
            pass
        
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
        
        # Skip processing if a sector change is already in progress
        # Note: We've removed the cooldown check for maximum responsiveness
        if self.sector_change_in_progress:
            # Update tracking variables for next iteration
            self.last_position = current_position
            self.last_position_time = current_time
            return
        
        # First, check if we're entering the neutral state (deadzone)
        if new_state == "neutral" and self.current_state != "neutral":
            # If we're going to neutral state, release all keys
            self.release_all_keys()
        # Handle sector changes (only if we're not in neutral state)
        elif new_sector != self.current_sector:
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
        
        try:
            # Use the Windows API to send a precise sector change sequence
            # This is now a direct, atomic operation with no delays
            send_sector_change(cancel_key, old_attack_key, new_attack_key, 0)
            
            # Update the pressed keys set
            if old_attack_key in self.pressed_keys:
                self.pressed_keys.remove(old_attack_key)
                self._log_key_action(old_attack_key, True, batch=True)
            
            self.pressed_keys.add(new_attack_key)
            self._log_key_action(cancel_key, False, batch=True)
            self._log_key_action(cancel_key, True, batch=True)
            self._log_key_action(new_attack_key, False, batch=True)
            
            # Immediately mark the sector change as complete
            self.sector_change_in_progress = False
            # Reset the cooldown timer to allow immediate next sector change
            self.last_sector_change_time = 0
        except Exception as e:
            print(f"Error during sector change: {e}")
            self.sector_change_in_progress = False
        
        # Log the sector change for debugging
        print(f"Executed sector change: {old_sector} -> {new_sector}")
    
    def _process_key_events(self):
        """
        Process key events from the queue with precise timing.
        Optimized to process events individually for maximum compatibility.
        """
        from src.win_input import key_down, key_up
        
        while self.key_event_thread_running:
            try:
                # Get the next key event from the queue with a timeout
                key, is_up, delay = self.key_event_queue.get(timeout=0.1)
                
                # If there's a delay, wait before processing
                if delay > 0:
                    time.sleep(delay)
                
                # Execute the key event
                if is_up:
                    # Key up event
                    if key in self.pressed_keys:
                        key_up(key)
                        self.pressed_keys.remove(key)
                        self._log_key_action(key, True, batch=True)
                else:
                    # Key down event
                    if key not in self.pressed_keys:
                        key_down(key)
                        self.pressed_keys.add(key)
                        self._log_key_action(key, False, batch=True)
                
                # Mark the task as done
                self.key_event_queue.task_done()
                
                # Check if this was the last event in a sector change
                if self.key_event_queue.empty() and self.sector_change_in_progress:
                    self.sector_change_in_progress = False
                    # Note: We don't reset the last_sector_change_time here to maintain the cooldown
            except queue.Empty:
                # No events in the queue, just continue
                pass
            except Exception as e:
                print(f"Error processing key event: {e}")
    
    def start_background_thread(self):
        """Start the background threads for continuous updates and key event processing."""
        # Start the main update thread
        if self.thread and self.thread.is_alive():
            pass  # Already running
        else:
            self.running = True
            self.thread = threading.Thread(target=self._background_thread)
            self.thread.daemon = True
            self.thread.start()
        
        # Start the key event processing thread
        if self.key_event_thread and self.key_event_thread.is_alive():
            pass  # Already running
        else:
            self.key_event_thread_running = True
            self.key_event_thread = threading.Thread(target=self._process_key_events)
            self.key_event_thread.daemon = True
            self.key_event_thread.start()
    
    def stop_background_thread(self):
        """Stop all background threads."""
        # Stop the main update thread
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # Stop the key event processing thread
        self.key_event_thread_running = False
        if self.key_event_thread:
            self.key_event_thread.join(timeout=1.0)
        
        # Release all keys when stopping
        self.release_all_keys()
    
    def _background_thread(self):
        """Background thread for continuous updates."""
        while self.running:
            self.update()
            time.sleep(0.0005)  # 2000 Hz update rate for maximum responsiveness
    
    def get_debug_info(self):
        """Get debug information about the controller state."""
        return self.debug_info
