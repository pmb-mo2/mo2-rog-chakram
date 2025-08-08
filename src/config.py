"""
Configuration settings for the Chakram X controller.
"""

import os
import json

# Default configuration values

# Joystick deadzone (0.0 to 1.0)
DEFAULT_DEADZONE = 0.15

# Time threshold for deadzone (in seconds) - how long to stay in deadzone before releasing attack
DEFAULT_DEADZONE_TIME_THRESHOLD = 0.05  # 50ms default

# Speed threshold for quick movement through deadzone (units per second)
DEFAULT_DEADZONE_SPEED_THRESHOLD = 0.05

# Delay between releasing attack button and cancel button (in seconds)
DEFAULT_RELEASE_DELAY = 0.00

# Cooldown period between sector changes (in seconds) - set to 0 for maximum responsiveness
DEFAULT_SECTOR_CHANGE_COOLDOWN = 0.0

# Adaptive control system settings
DEFAULT_ADAPTIVE_ENABLED = True

# Dynamic deadzone settings
DEFAULT_DYNAMIC_DEADZONE_ENABLED = False
DEFAULT_DYNAMIC_DEADZONE_MIN_FACTOR = 1.5  # Minimum multiplier for deadzone (fast movements)
DEFAULT_DYNAMIC_DEADZONE_MAX_FACTOR = 1.5  # Maximum multiplier for deadzone (slow movements)

# Movement prediction settings
DEFAULT_PREDICTION_ENABLED = True
DEFAULT_PREDICTION_TIME = 0.05  # Time in seconds to predict ahead
DEFAULT_PREDICTION_CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence to use predictions

# Transition smoothness settings
DEFAULT_TRANSITION_SMOOTHNESS = 0.1  # Base smoothness value
DEFAULT_TRANSITION_MIN_FACTOR = 0.5  # Minimum multiplier for smoothness (fast movements)
DEFAULT_TRANSITION_MAX_FACTOR = 2.0  # Maximum multiplier for smoothness (slow movements)

# Combat mode settings
DEFAULT_COMBAT_MODE_ENABLED = True
DEFAULT_COMBAT_MODE_KEY = "c"  # Key to toggle combat mode
DEFAULT_COMBAT_MODE_DEADZONE = 0.1  # Smaller deadzone for combat mode
DEFAULT_COMBAT_MODE_TRANSITION_SMOOTHNESS = 0.05  # Faster transitions for combat mode

# Alternative mode settings
DEFAULT_ALT_MODE_KEY = "alt"  # Default key to activate alternative mode
DEFAULT_ALT_MODE_CURSOR_OFFSET = 20  # Default cursor movement distance in pixels

# Mouse axes settings
DEFAULT_USE_MOUSE_AXES = False
DEFAULT_MOUSE_AXES_MODIFIERS = []
DEFAULT_MOUSE_AXES_POINTER_LOCK = True
DEFAULT_MOUSE_AXES_LOCK_CENTER = True
DEFAULT_MOUSE_AXES_INVERT_Y = False
DEFAULT_ATTACK_ON_MODIFIER_RELEASE = True
DEFAULT_AIM_MODIFIER = "alt"
DEFAULT_AIM_REQUIRES_MOVEMENT = True
DEFAULT_AIM_DIRECTION_MEMORY_MS = 250
DEFAULT_ATTACK_PRESS_DURATION_MS = 50
DEFAULT_POST_ATTACK_COOLDOWN_MS = 200
DEFAULT_BLOCK_WHILE_HELD = True
DEFAULT_BLOCK_KEY = "right_mouse"

# Game state detection settings
DEFAULT_GAME_STATE_DETECTION_ENABLED = True
DEFAULT_COMBAT_TIMEOUT = 5.0  # Time in seconds after last combat action to exit combat state

# Sector definitions (in degrees, 0° is right, 90° is down)
DEFAULT_SECTORS = {
    "overhead": {"start": 225, "end": 315},       # Left sector (225° to 315°)
    "right": {"start": 315, "end": 45},    # Top sector (315° to 45°)
    "thrust": {"start": 45, "end": 135},   # Right sector (45° to 135°)
    "left": {"start": 135, "end": 225}       # Bottom sector (135° to 225°)
}

# Sector definitions (in degrees, 0° is right, 90° is down)
# The controller will handle sector transitions automatically
# When crossing sector boundaries, it will:
# 1. Press the cancel key
# 2. Release the previous attack key
# 3. Release the cancel key after a delay
# 4. Press the new attack key

# Key mappings for each action
DEFAULT_KEY_MAPPINGS = {
    "overhead": "up",    # Overhead attack key
    "right": "right",       # Right attack key
    "thrust": "down",   # thrust attack key
    "left": "left",        # Left attack key
    "cancel": "middle_mouse",  # Cancel key (using middle mouse button)
    "alt_mode": "alt"  # Alternative mode activation key
}

# Default visualization settings
DEFAULT_VISUALIZATION = {
    "window_size": (800, 600),
    "background_color": (30, 30, 30),
    "text_color": (200, 200, 200),
    "joystick_color": (0, 255, 0),
    "sector_colors": {
        "overhead": (255, 100, 100),
        "right": (100, 255, 100),
        "thrust": (100, 100, 255),
        "left": (255, 255, 100)
    },
    "state_colors": {
        "neutral": (100, 100, 100),
        "cancel": (255, 165, 0),
        "attack": (255, 0, 0)
    }
}

# Try to load the user's configuration
def load_user_config():
    """Load the user's configuration from the config file."""
    config_dir = os.path.join(os.path.expanduser("~"), ".chakram_controller")
    config_path = os.path.join(config_dir, "config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            
            # Return the user's configuration
            return {
                "deadzone": user_config.get("deadzone", DEFAULT_DEADZONE),
                "deadzone_time_threshold": user_config.get("deadzone_time_threshold", DEFAULT_DEADZONE_TIME_THRESHOLD),
                "deadzone_speed_threshold": user_config.get("deadzone_speed_threshold", DEFAULT_DEADZONE_SPEED_THRESHOLD),
                "release_delay": user_config.get("release_delay", DEFAULT_RELEASE_DELAY),
                "sector_change_cooldown": user_config.get("sector_change_cooldown", DEFAULT_SECTOR_CHANGE_COOLDOWN),
                "alt_mode_key": user_config.get("alt_mode_key", DEFAULT_ALT_MODE_KEY),
                "alt_mode_cursor_offset": user_config.get("alt_mode_cursor_offset", DEFAULT_ALT_MODE_CURSOR_OFFSET),
                "use_mouse_axes": user_config.get("use_mouse_axes", DEFAULT_USE_MOUSE_AXES),
                "mouse_axes_modifiers": user_config.get("mouse_axes_modifiers", DEFAULT_MOUSE_AXES_MODIFIERS),
                "mouse_axes_pointer_lock": user_config.get("mouse_axes_pointer_lock", DEFAULT_MOUSE_AXES_POINTER_LOCK),
                "mouse_axes_lock_center": user_config.get("mouse_axes_lock_center", DEFAULT_MOUSE_AXES_LOCK_CENTER),
                "mouse_axes_invert_y": user_config.get("mouse_axes_invert_y", DEFAULT_MOUSE_AXES_INVERT_Y),
                "attack_on_modifier_release": user_config.get("attack_on_modifier_release", DEFAULT_ATTACK_ON_MODIFIER_RELEASE),
                "aim_modifier": user_config.get("aim_modifier", DEFAULT_AIM_MODIFIER),
                "aim_requires_movement": user_config.get("aim_requires_movement", DEFAULT_AIM_REQUIRES_MOVEMENT),
                "aim_direction_memory_ms": user_config.get("aim_direction_memory_ms", DEFAULT_AIM_DIRECTION_MEMORY_MS),
                "attack_press_duration_ms": user_config.get("attack_press_duration_ms", DEFAULT_ATTACK_PRESS_DURATION_MS),
                "post_attack_cooldown_ms": user_config.get("post_attack_cooldown_ms", DEFAULT_POST_ATTACK_COOLDOWN_MS),
                "block_while_held": user_config.get("block_while_held", DEFAULT_BLOCK_WHILE_HELD),
                "block_key": user_config.get("block_key", DEFAULT_BLOCK_KEY),
                "sectors": user_config.get("sectors", DEFAULT_SECTORS),
                "key_mappings": user_config.get("key_mappings", DEFAULT_KEY_MAPPINGS),
                "visualization": user_config.get("visualization", DEFAULT_VISUALIZATION),
                
                # Adaptive control system settings
                "adaptive_enabled": user_config.get("adaptive_enabled", DEFAULT_ADAPTIVE_ENABLED),
                
                # Dynamic deadzone settings
                "dynamic_deadzone_enabled": user_config.get("dynamic_deadzone_enabled", DEFAULT_DYNAMIC_DEADZONE_ENABLED),
                "dynamic_deadzone_min_factor": user_config.get("dynamic_deadzone_min_factor", DEFAULT_DYNAMIC_DEADZONE_MIN_FACTOR),
                "dynamic_deadzone_max_factor": user_config.get("dynamic_deadzone_max_factor", DEFAULT_DYNAMIC_DEADZONE_MAX_FACTOR),
                
                # Movement prediction settings
                "prediction_enabled": user_config.get("prediction_enabled", DEFAULT_PREDICTION_ENABLED),
                "prediction_time": user_config.get("prediction_time", DEFAULT_PREDICTION_TIME),
                "prediction_confidence_threshold": user_config.get("prediction_confidence_threshold", DEFAULT_PREDICTION_CONFIDENCE_THRESHOLD),
                
                # Transition smoothness settings
                "transition_smoothness": user_config.get("transition_smoothness", DEFAULT_TRANSITION_SMOOTHNESS),
                "transition_min_factor": user_config.get("transition_min_factor", DEFAULT_TRANSITION_MIN_FACTOR),
                "transition_max_factor": user_config.get("transition_max_factor", DEFAULT_TRANSITION_MAX_FACTOR),
                
                # Combat mode settings
                "combat_mode_enabled": user_config.get("combat_mode_enabled", DEFAULT_COMBAT_MODE_ENABLED),
                "combat_mode_key": user_config.get("combat_mode_key", DEFAULT_COMBAT_MODE_KEY),
                "combat_mode_deadzone": user_config.get("combat_mode_deadzone", DEFAULT_COMBAT_MODE_DEADZONE),
                "combat_mode_transition_smoothness": user_config.get("combat_mode_transition_smoothness", DEFAULT_COMBAT_MODE_TRANSITION_SMOOTHNESS),
                
                # Game state detection settings
                "game_state_detection_enabled": user_config.get("game_state_detection_enabled", DEFAULT_GAME_STATE_DETECTION_ENABLED),
                "combat_timeout": user_config.get("combat_timeout", DEFAULT_COMBAT_TIMEOUT)
            }
        except Exception as e:
            print(f"Error loading user configuration: {e}")
    
    # Return the default configuration if the user's configuration couldn't be loaded
    return {
        "deadzone": DEFAULT_DEADZONE,
        "deadzone_time_threshold": DEFAULT_DEADZONE_TIME_THRESHOLD,
        "deadzone_speed_threshold": DEFAULT_DEADZONE_SPEED_THRESHOLD,
        "release_delay": DEFAULT_RELEASE_DELAY,
        "sector_change_cooldown": DEFAULT_SECTOR_CHANGE_COOLDOWN,
        "use_mouse_axes": DEFAULT_USE_MOUSE_AXES,
        "mouse_axes_modifiers": DEFAULT_MOUSE_AXES_MODIFIERS,
        "mouse_axes_pointer_lock": DEFAULT_MOUSE_AXES_POINTER_LOCK,
        "mouse_axes_lock_center": DEFAULT_MOUSE_AXES_LOCK_CENTER,
        "mouse_axes_invert_y": DEFAULT_MOUSE_AXES_INVERT_Y,
        "attack_on_modifier_release": DEFAULT_ATTACK_ON_MODIFIER_RELEASE,
        "aim_modifier": DEFAULT_AIM_MODIFIER,
        "aim_requires_movement": DEFAULT_AIM_REQUIRES_MOVEMENT,
        "aim_direction_memory_ms": DEFAULT_AIM_DIRECTION_MEMORY_MS,
        "attack_press_duration_ms": DEFAULT_ATTACK_PRESS_DURATION_MS,
        "post_attack_cooldown_ms": DEFAULT_POST_ATTACK_COOLDOWN_MS,
        "block_while_held": DEFAULT_BLOCK_WHILE_HELD,
        "block_key": DEFAULT_BLOCK_KEY,
        "sectors": DEFAULT_SECTORS,
        "key_mappings": DEFAULT_KEY_MAPPINGS,
        "visualization": DEFAULT_VISUALIZATION,
        
        # Adaptive control system settings
        "adaptive_enabled": DEFAULT_ADAPTIVE_ENABLED,
        
        # Dynamic deadzone settings
        "dynamic_deadzone_enabled": DEFAULT_DYNAMIC_DEADZONE_ENABLED,
        "dynamic_deadzone_min_factor": DEFAULT_DYNAMIC_DEADZONE_MIN_FACTOR,
        "dynamic_deadzone_max_factor": DEFAULT_DYNAMIC_DEADZONE_MAX_FACTOR,
        
        # Movement prediction settings
        "prediction_enabled": DEFAULT_PREDICTION_ENABLED,
        "prediction_time": DEFAULT_PREDICTION_TIME,
        "prediction_confidence_threshold": DEFAULT_PREDICTION_CONFIDENCE_THRESHOLD,
        
        # Transition smoothness settings
        "transition_smoothness": DEFAULT_TRANSITION_SMOOTHNESS,
        "transition_min_factor": DEFAULT_TRANSITION_MIN_FACTOR,
        "transition_max_factor": DEFAULT_TRANSITION_MAX_FACTOR,
        
        # Combat mode settings
        "combat_mode_enabled": DEFAULT_COMBAT_MODE_ENABLED,
        "combat_mode_key": DEFAULT_COMBAT_MODE_KEY,
        "combat_mode_deadzone": DEFAULT_COMBAT_MODE_DEADZONE,
        "combat_mode_transition_smoothness": DEFAULT_COMBAT_MODE_TRANSITION_SMOOTHNESS,
        
        # Game state detection settings
        "game_state_detection_enabled": DEFAULT_GAME_STATE_DETECTION_ENABLED,
        "combat_timeout": DEFAULT_COMBAT_TIMEOUT
    }

# Load the user's configuration
user_config = load_user_config()

# Set the configuration values
DEADZONE = user_config["deadzone"]
DEADZONE_TIME_THRESHOLD = user_config.get("deadzone_time_threshold", DEFAULT_DEADZONE_TIME_THRESHOLD)
DEADZONE_SPEED_THRESHOLD = user_config.get("deadzone_speed_threshold", DEFAULT_DEADZONE_SPEED_THRESHOLD)
RELEASE_DELAY = user_config["release_delay"]
SECTOR_CHANGE_COOLDOWN = user_config.get("sector_change_cooldown", DEFAULT_SECTOR_CHANGE_COOLDOWN)
ALT_MODE_KEY = user_config.get("alt_mode_key", DEFAULT_ALT_MODE_KEY)
ALT_MODE_CURSOR_OFFSET = user_config.get("alt_mode_cursor_offset", DEFAULT_ALT_MODE_CURSOR_OFFSET)
USE_MOUSE_AXES = user_config.get("use_mouse_axes", DEFAULT_USE_MOUSE_AXES)
MOUSE_AXES_MODIFIERS = user_config.get("mouse_axes_modifiers", DEFAULT_MOUSE_AXES_MODIFIERS)
MOUSE_AXES_POINTER_LOCK = user_config.get("mouse_axes_pointer_lock", DEFAULT_MOUSE_AXES_POINTER_LOCK)
MOUSE_AXES_LOCK_CENTER = user_config.get("mouse_axes_lock_center", DEFAULT_MOUSE_AXES_LOCK_CENTER)
MOUSE_AXES_INVERT_Y = user_config.get("mouse_axes_invert_y", DEFAULT_MOUSE_AXES_INVERT_Y)
ATTACK_ON_MODIFIER_RELEASE = user_config.get("attack_on_modifier_release", DEFAULT_ATTACK_ON_MODIFIER_RELEASE)
AIM_MODIFIER = user_config.get("aim_modifier", DEFAULT_AIM_MODIFIER)
AIM_REQUIRES_MOVEMENT = user_config.get("aim_requires_movement", DEFAULT_AIM_REQUIRES_MOVEMENT)
AIM_DIRECTION_MEMORY_MS = user_config.get("aim_direction_memory_ms", DEFAULT_AIM_DIRECTION_MEMORY_MS)
ATTACK_PRESS_DURATION_MS = user_config.get("attack_press_duration_ms", DEFAULT_ATTACK_PRESS_DURATION_MS)
POST_ATTACK_COOLDOWN_MS = user_config.get("post_attack_cooldown_ms", DEFAULT_POST_ATTACK_COOLDOWN_MS)
BLOCK_WHILE_HELD = user_config.get("block_while_held", DEFAULT_BLOCK_WHILE_HELD)
BLOCK_KEY = user_config.get("block_key", DEFAULT_BLOCK_KEY)
SECTORS = user_config["sectors"]
KEY_MAPPINGS = user_config["key_mappings"]
VISUALIZATION = user_config["visualization"]

# Adaptive control system settings
ADAPTIVE_ENABLED = user_config.get("adaptive_enabled", DEFAULT_ADAPTIVE_ENABLED)

# Dynamic deadzone settings
DYNAMIC_DEADZONE_ENABLED = user_config.get("dynamic_deadzone_enabled", DEFAULT_DYNAMIC_DEADZONE_ENABLED)
DYNAMIC_DEADZONE_MIN_FACTOR = user_config.get("dynamic_deadzone_min_factor", DEFAULT_DYNAMIC_DEADZONE_MIN_FACTOR)
DYNAMIC_DEADZONE_MAX_FACTOR = user_config.get("dynamic_deadzone_max_factor", DEFAULT_DYNAMIC_DEADZONE_MAX_FACTOR)

# Movement prediction settings
PREDICTION_ENABLED = user_config.get("prediction_enabled", DEFAULT_PREDICTION_ENABLED)
PREDICTION_TIME = user_config.get("prediction_time", DEFAULT_PREDICTION_TIME)
PREDICTION_CONFIDENCE_THRESHOLD = user_config.get("prediction_confidence_threshold", DEFAULT_PREDICTION_CONFIDENCE_THRESHOLD)

# Transition smoothness settings
TRANSITION_SMOOTHNESS = user_config.get("transition_smoothness", DEFAULT_TRANSITION_SMOOTHNESS)
TRANSITION_MIN_FACTOR = user_config.get("transition_min_factor", DEFAULT_TRANSITION_MIN_FACTOR)
TRANSITION_MAX_FACTOR = user_config.get("transition_max_factor", DEFAULT_TRANSITION_MAX_FACTOR)

# Combat mode settings
COMBAT_MODE_ENABLED = user_config.get("combat_mode_enabled", DEFAULT_COMBAT_MODE_ENABLED)
COMBAT_MODE_KEY = user_config.get("combat_mode_key", DEFAULT_COMBAT_MODE_KEY)
COMBAT_MODE_DEADZONE = user_config.get("combat_mode_deadzone", DEFAULT_COMBAT_MODE_DEADZONE)
COMBAT_MODE_TRANSITION_SMOOTHNESS = user_config.get("combat_mode_transition_smoothness", DEFAULT_COMBAT_MODE_TRANSITION_SMOOTHNESS)

# Game state detection settings
GAME_STATE_DETECTION_ENABLED = user_config.get("game_state_detection_enabled", DEFAULT_GAME_STATE_DETECTION_ENABLED)
COMBAT_TIMEOUT = user_config.get("combat_timeout", DEFAULT_COMBAT_TIMEOUT)
