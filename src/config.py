"""
Configuration settings for the Chakram X controller.
"""

import os
import json

# Default configuration values

# Joystick deadzone (0.0 to 1.0)
DEFAULT_DEADZONE = 0.15

# Time threshold for deadzone (in seconds) - how long to stay in deadzone before releasing attack
DEFAULT_DEADZONE_TIME_THRESHOLD = 0.05  # 10ms default

# Speed threshold for quick movement through deadzone (units per second)
DEFAULT_DEADZONE_SPEED_THRESHOLD = 0.05

# Delay between releasing attack button and cancel button (in seconds)
DEFAULT_RELEASE_DELAY = 0.00

# Cooldown period between sector changes (in seconds) - set to 0 for maximum responsiveness
DEFAULT_SECTOR_CHANGE_COOLDOWN = 0.0

# Alternative mode settings
DEFAULT_ALT_MODE_KEY = "alt"  # Default key to activate alternative mode
DEFAULT_ALT_MODE_CURSOR_OFFSET = 50  # Default cursor movement distance in pixels

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
                "sectors": user_config.get("sectors", DEFAULT_SECTORS),
                "key_mappings": user_config.get("key_mappings", DEFAULT_KEY_MAPPINGS),
                "visualization": user_config.get("visualization", DEFAULT_VISUALIZATION)
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
        "sectors": DEFAULT_SECTORS,
        "key_mappings": DEFAULT_KEY_MAPPINGS,
        "visualization": DEFAULT_VISUALIZATION
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
SECTORS = user_config["sectors"]
KEY_MAPPINGS = user_config["key_mappings"]
VISUALIZATION = user_config["visualization"]
