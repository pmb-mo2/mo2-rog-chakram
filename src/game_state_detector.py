"""
Game state detector module for the Chakram X controller.
Detects the current game state (combat, exploration) based on input patterns.
"""

import time

class GameStateDetector:
    """
    Detects the current game state based on input patterns.
    Used to adapt control behavior based on the current game context.
    """
    
    def __init__(self, combat_timeout=5.0):
        """
        Initialize the game state detector.
        
        Args:
            combat_timeout (float): Time in seconds after last combat action to exit combat state
        """
        self.current_state = "exploration"  # Default state: "exploration" or "combat"
        self.last_combat_action_time = 0
        self.combat_timeout = combat_timeout
        
        # Combat action tracking
        self.combat_actions = set()
        self.combat_action_history = []
        self.max_history_size = 20
        
        # Combat detection settings
        self.combat_keys = ["up", "down", "left", "right", "middle_mouse"]
        
    def update(self, pressed_keys, current_time):
        """
        Update the game state based on current inputs.
        
        Args:
            pressed_keys (set): Set of currently pressed keys
            current_time (float): Current timestamp
            
        Returns:
            str: Current game state ("exploration" or "combat")
        """
        # Check for combat actions
        combat_action_detected = False
        
        # Check if any combat keys are pressed
        for key in self.combat_keys:
            if key in pressed_keys:
                combat_action_detected = True
                self.combat_actions.add(key)
                
                # Add to history with timestamp
                self.combat_action_history.append((key, current_time))
                
                # Trim history if needed
                if len(self.combat_action_history) > self.max_history_size:
                    self.combat_action_history.pop(0)
                
                # Update last combat action time
                self.last_combat_action_time = current_time
                break
        
        # Determine current state
        time_since_last_combat = current_time - self.last_combat_action_time
        
        if combat_action_detected or time_since_last_combat < self.combat_timeout:
            # In combat state
            if self.current_state != "combat":
                print(f"Entering combat state at {current_time:.3f}")
                self.current_state = "combat"
        else:
            # In exploration state
            if self.current_state != "exploration":
                print(f"Entering exploration state at {current_time:.3f}")
                self.current_state = "exploration"
        
        return self.current_state
    
    def get_combat_intensity(self, current_time, window_size=3.0):
        """
        Calculate the current combat intensity based on action frequency.
        
        Args:
            current_time (float): Current timestamp
            window_size (float): Time window to consider for intensity calculation
            
        Returns:
            float: Combat intensity from 0.0 to 1.0
        """
        # Count actions within the time window
        recent_actions = 0
        
        for action, timestamp in self.combat_action_history:
            if current_time - timestamp <= window_size:
                recent_actions += 1
        
        # Calculate intensity (normalize by expected max actions in window)
        # Assuming max 10 actions in a 3-second window for max intensity
        max_expected_actions = 10 * (window_size / 3.0)
        intensity = min(1.0, recent_actions / max_expected_actions)
        
        return intensity
    
    def is_in_combat(self):
        """
        Check if currently in combat state.
        
        Returns:
            bool: True if in combat state, False otherwise
        """
        return self.current_state == "combat"
    
    def get_optimal_deadzone(self, base_deadzone, combat_deadzone):
        """
        Get the optimal deadzone size based on current state.
        
        Args:
            base_deadzone (float): Base deadzone size for exploration
            combat_deadzone (float): Deadzone size for combat
            
        Returns:
            float: Optimal deadzone size for current state
        """
        if self.is_in_combat():
            return combat_deadzone
        else:
            return base_deadzone
    
    def get_optimal_transition_smoothness(self, base_smoothness, combat_smoothness):
        """
        Get the optimal transition smoothness based on current state.
        
        Args:
            base_smoothness (float): Base smoothness for exploration
            combat_smoothness (float): Smoothness for combat
            
        Returns:
            float: Optimal transition smoothness for current state
        """
        if self.is_in_combat():
            return combat_smoothness
        else:
            return base_smoothness
