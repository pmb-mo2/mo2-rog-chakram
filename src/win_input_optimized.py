"""
Optimized Windows input module using interception-python for direct key simulation.
This module is specifically optimized for high-speed button presses.
"""

import time
import ctypes
import sys
from ctypes import wintypes

# Try to import interception-python, but handle the case where it's not available
INTERCEPTION_AVAILABLE = False
try:
    import interception
    INTERCEPTION_AVAILABLE = True
    print("Interception driver loaded successfully.")
except (ImportError, Exception) as e:
    print(f"Warning: Could not initialize Interception driver: {e}")
    print("Falling back to Windows API for input simulation.")

# Windows API constants
INPUT_KEYBOARD = 1
INPUT_MOUSE = 0
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

# Virtual key codes (for Windows API fallback)
VK_CODES = {
    'left': 0x25,  # VK_LEFT
    'up': 0x26,    # VK_UP
    'right': 0x27, # VK_RIGHT
    'down': 0x28,  # VK_DOWN
    'c': 0x43,     # C key
    'esc': 0x1B,   # ESC key
    # Add more keys as needed
}

# Define input structures for Windows API
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]

# Load user32.dll for Windows API
user32 = ctypes.WinDLL('user32', use_last_error=True)
SendInput = user32.SendInput
SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), wintypes.INT)
SendInput.restype = wintypes.UINT

# Initialize Interception devices
keyboard = None
mouse = None
initialized = False

def initialize():
    """Initialize the Interception devices or fallback to Windows API."""
    global keyboard, mouse, initialized
    
    if initialized:
        return True
    
    if not INTERCEPTION_AVAILABLE:
        print("Interception driver not available. Using Windows API fallback.")
        return False
    
    try:
        # Get keyboard and mouse devices
        keyboard = interception.get_keyboard()
        mouse = interception.get_mouse()
        
        if keyboard is None:
            print("No keyboard found")
            return False
        
        if mouse is None:
            print("No mouse found")
            return False
        
        print(f"Found keyboard at device ID {keyboard}")
        print(f"Found mouse at device ID {mouse}")
        
        initialized = True
        return True
    except Exception as e:
        print(f"Error initializing Interception: {e}")
        return False

def cleanup():
    """Clean up the Interception resources."""
    global initialized
    initialized = False

# Optimized key functions for interception
def key_down_interception(key):
    """Send a key down event using Interception."""
    try:
        interception.key_down(key)
        return True
    except Exception as e:
        print(f"Error sending key down event with Interception: {e}")
        return False

def key_up_interception(key):
    """Send a key up event using Interception."""
    try:
        interception.key_up(key)
        return True
    except Exception as e:
        print(f"Error sending key up event with Interception: {e}")
        return False

def mouse_down_interception(button):
    """Send a mouse button down event using Interception."""
    try:
        interception.mouse_down(button)
        return True
    except Exception as e:
        print(f"Error sending mouse down event with Interception: {e}")
        return False

def mouse_up_interception(button):
    """Send a mouse button up event using Interception."""
    try:
        interception.mouse_up(button)
        return True
    except Exception as e:
        print(f"Error sending mouse up event with Interception: {e}")
        return False

# Windows API fallback functions
def create_key_input(key, is_up):
    """Create an INPUT structure for a key event (Windows API)."""
    if key not in VK_CODES:
        print(f"Error: Key '{key}' not found in VK_CODES")
        return None
    
    vk_code = VK_CODES[key]
    
    return INPUT(
        type=INPUT_KEYBOARD,
        union=INPUT_UNION(
            ki=KEYBDINPUT(
                wVk=vk_code,
                wScan=0,
                dwFlags=KEYEVENTF_KEYUP if is_up else 0,
                time=0,
                dwExtraInfo=ctypes.pointer(wintypes.ULONG(0))
            )
        )
    )

def create_mouse_input(button, is_down):
    """Create an INPUT structure for a mouse button event (Windows API)."""
    if button == 'left':
        flag = MOUSEEVENTF_LEFTDOWN if is_down else MOUSEEVENTF_LEFTUP
    elif button == 'right':
        flag = MOUSEEVENTF_RIGHTDOWN if is_down else MOUSEEVENTF_RIGHTUP
    elif button == 'middle':
        flag = MOUSEEVENTF_MIDDLEDOWN if is_down else MOUSEEVENTF_MIDDLEUP
    else:
        print(f"Error: Unknown mouse button '{button}'")
        return None
    
    return INPUT(
        type=INPUT_MOUSE,
        union=INPUT_UNION(
            mi=MOUSEINPUT(
                dx=0,
                dy=0,
                mouseData=0,
                dwFlags=flag,
                time=0,
                dwExtraInfo=ctypes.pointer(wintypes.ULONG(0))
            )
        )
    )

def key_down_windows_api(key):
    """Send a key down event using the Windows API."""
    try:
        input_struct = create_key_input(key, False)
        if not input_struct:
            return False
        
        result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending key down event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending key down event: {e}")
        return False

def key_up_windows_api(key):
    """Send a key up event using the Windows API."""
    try:
        input_struct = create_key_input(key, True)
        if not input_struct:
            return False
        
        result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending key up event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending key up event: {e}")
        return False

def mouse_button_down_windows_api(button):
    """Send a mouse button down event using Windows API."""
    try:
        input_struct = create_mouse_input(button, True)
        if not input_struct:
            return False
        
        result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending {button} mouse down event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending {button} mouse down event: {e}")
        return False

def mouse_button_up_windows_api(button):
    """Send a mouse button up event using Windows API."""
    try:
        input_struct = create_mouse_input(button, False)
        if not input_struct:
            return False
        
        result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending {button} mouse up event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending {button} mouse up event: {e}")
        return False

# Main input functions that use Interception or fallback to Windows API
def key_down(key):
    """Send a key down event using Interception or Windows API fallback."""
    if not INTERCEPTION_AVAILABLE:
        return key_down_windows_api(key)
    
    if not initialized:
        if not initialize():
            return key_down_windows_api(key)
    
    return key_down_interception(key)

def key_up(key):
    """Send a key up event using Interception or Windows API fallback."""
    if not INTERCEPTION_AVAILABLE:
        return key_up_windows_api(key)
    
    if not initialized:
        if not initialize():
            return key_up_windows_api(key)
    
    return key_up_interception(key)

def press_key(key):
    """Press and release a key as a single atomic operation."""
    if not INTERCEPTION_AVAILABLE:
        if not key_down_windows_api(key):
            return False
        if not key_up_windows_api(key):
            return False
        return True
    
    if not initialized:
        if not initialize():
            if not key_down_windows_api(key):
                return False
            if not key_up_windows_api(key):
                return False
            return True
    
    try:
        interception.press(key)
        return True
    except Exception as e:
        print(f"Error pressing key with Interception: {e}")
        if not key_down_windows_api(key):
            return False
        if not key_up_windows_api(key):
            return False
        return True

def left_mouse_down():
    """Send a left mouse button down event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_down_windows_api('left')
    
    if not initialized:
        if not initialize():
            return mouse_button_down_windows_api('left')
    
    return mouse_down_interception('left')

def left_mouse_up():
    """Send a left mouse button up event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_up_windows_api('left')
    
    if not initialized:
        if not initialize():
            return mouse_button_up_windows_api('left')
    
    return mouse_up_interception('left')

def click_left_mouse():
    """Click the left mouse button (press and release)."""
    if not INTERCEPTION_AVAILABLE:
        if not mouse_button_down_windows_api('left'):
            return False
        if not mouse_button_up_windows_api('left'):
            return False
        return True
    
    if not initialized:
        if not initialize():
            if not mouse_button_down_windows_api('left'):
                return False
            if not mouse_button_up_windows_api('left'):
                return False
            return True
    
    try:
        interception.left_click()
        return True
    except Exception as e:
        print(f"Error clicking left mouse with Interception: {e}")
        if not mouse_button_down_windows_api('left'):
            return False
        if not mouse_button_up_windows_api('left'):
            return False
        return True

def middle_mouse_down():
    """Send a middle mouse button down event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_down_windows_api('middle')
    
    if not initialized:
        if not initialize():
            return mouse_button_down_windows_api('middle')
    
    return mouse_down_interception('middle')

def middle_mouse_up():
    """Send a middle mouse button up event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_up_windows_api('middle')
    
    if not initialized:
        if not initialize():
            return mouse_button_up_windows_api('middle')
    
    return mouse_up_interception('middle')

def click_middle_mouse():
    """Click the middle mouse button (press and release)."""
    if not INTERCEPTION_AVAILABLE:
        if not mouse_button_down_windows_api('middle'):
            return False
        if not mouse_button_up_windows_api('middle'):
            return False
        return True
    
    if not initialized:
        if not initialize():
            if not mouse_button_down_windows_api('middle'):
                return False
            if not mouse_button_up_windows_api('middle'):
                return False
            return True
    
    try:
        interception.click('middle')
        return True
    except Exception as e:
        print(f"Error clicking middle mouse with Interception: {e}")
        if not mouse_button_down_windows_api('middle'):
            return False
        if not mouse_button_up_windows_api('middle'):
            return False
        return True

def right_mouse_down():
    """Send a right mouse button down event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_down_windows_api('right')
    
    if not initialized:
        if not initialize():
            return mouse_button_down_windows_api('right')
    
    return mouse_down_interception('right')

def right_mouse_up():
    """Send a right mouse button up event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_up_windows_api('right')
    
    if not initialized:
        if not initialize():
            return mouse_button_up_windows_api('right')
    
    return mouse_up_interception('right')

def click_right_mouse():
    """Click the right mouse button (press and release)."""
    if not INTERCEPTION_AVAILABLE:
        if not mouse_button_down_windows_api('right'):
            return False
        if not mouse_button_up_windows_api('right'):
            return False
        return True
    
    if not initialized:
        if not initialize():
            if not mouse_button_down_windows_api('right'):
                return False
            if not mouse_button_up_windows_api('right'):
                return False
            return True
    
    try:
        interception.right_click()
        return True
    except Exception as e:
        print(f"Error clicking right mouse with Interception: {e}")
        if not mouse_button_down_windows_api('right'):
            return False
        if not mouse_button_up_windows_api('right'):
            return False
        return True

def send_key_sequence(keys, delay=0.01):
    """
    Send a sequence of key events with precise timing.
    
    Args:
        keys (list): List of (key, is_up) tuples
        delay (float): Delay between key events. If 0, all events are sent atomically.
    
    Returns:
        bool: True if all events were sent successfully, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Windows API implementation
        if delay <= 0:
            # Create an array of inputs for atomic sending
            inputs = (INPUT * len(keys))()
            
            for i, (key, is_up) in enumerate(keys):
                if key not in VK_CODES:
                    print(f"Error: Key '{key}' not found in VK_CODES")
                    continue
                
                inputs[i] = INPUT(
                    type=INPUT_KEYBOARD,
                    union=INPUT_UNION(
                        ki=KEYBDINPUT(
                            wVk=VK_CODES[key],
                            wScan=0,
                            dwFlags=KEYEVENTF_KEYUP if is_up else 0,
                            time=0,
                            dwExtraInfo=ctypes.pointer(wintypes.ULONG(0))
                        )
                    )
                )
            
            result = SendInput(len(keys), ctypes.byref(inputs), ctypes.sizeof(INPUT))
            return result == len(keys)
        else:
            # Send with delay
            for key, is_up in keys:
                if is_up:
                    if not key_up_windows_api(key):
                        return False
                else:
                    if not key_down_windows_api(key):
                        return False
                
                time.sleep(delay)
            
            return True
    
    if not initialized:
        if not initialize():
            return send_key_sequence_windows_api(keys, delay)
    
    try:
        # Interception implementation
        if delay <= 0:
            # Send all at once (as fast as possible)
            for key, is_up in keys:
                if is_up:
                    interception.key_up(key)
                else:
                    interception.key_down(key)
        else:
            # Send with delay
            for key, is_up in keys:
                if is_up:
                    interception.key_up(key)
                else:
                    interception.key_down(key)
                
                time.sleep(delay)
        
        return True
    except Exception as e:
        print(f"Error sending key sequence with Interception: {e}")
        # Fallback to Windows API
        return send_key_sequence_windows_api(keys, delay)

def send_sector_change(cancel_key, old_attack_key, new_attack_key, release_delay=0.0):
    """
    Send a precise sector change sequence as a single atomic operation for maximum speed.
    
    Args:
        cancel_key (str): The cancel key or "middle_mouse" for middle mouse button
        old_attack_key (str): The old attack key
        new_attack_key (str): The new attack key
        release_delay (float): Optional delay between key events (default: 0.0)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Windows API implementation
        if cancel_key == "middle_mouse":
            if not mouse_button_down_windows_api('middle'):
                return False
            if not key_up_windows_api(old_attack_key):
                return False
            if not mouse_button_up_windows_api('middle'):
                return False
            if not key_down_windows_api(new_attack_key):
                return False
        else:
            if not key_down_windows_api(cancel_key):
                return False
            if not key_up_windows_api(old_attack_key):
                return False
            if not key_up_windows_api(cancel_key):
                return False
            if not key_down_windows_api(new_attack_key):
                return False
        
        return True
    
    if not initialized:
        if not initialize():
            # Fallback to Windows API
            return send_sector_change_windows_api(cancel_key, old_attack_key, new_attack_key)
    
    try:
        # Interception implementation - optimized for speed
        if cancel_key == "middle_mouse":
            # Use middle mouse button
            interception.mouse_down('middle')
            interception.key_up(old_attack_key)
            interception.mouse_up('middle')
            interception.key_down(new_attack_key)
        else:
            # Use keyboard key for cancel
            interception.key_down(cancel_key)
            interception.key_up(old_attack_key)
            interception.key_up(cancel_key)
            interception.key_down(new_attack_key)
        
        return True
    except Exception as e:
        print(f"Error sending sector change with Interception: {e}")
        # Fallback to Windows API
        if cancel_key == "middle_mouse":
            if not mouse_button_down_windows_api('middle'):
                return False
            if not key_up_windows_api(old_attack_key):
                return False
            if not mouse_button_up_windows_api('middle'):
                return False
            if not key_down_windows_api(new_attack_key):
                return False
        else:
            if not key_down_windows_api(cancel_key):
                return False
            if not key_up_windows_api(old_attack_key):
                return False
            if not key_up_windows_api(cancel_key):
                return False
            if not key_down_windows_api(new_attack_key):
                return False
        
        return True

# Batch operations for maximum performance
def send_batch_operations(operations):
    """
    Send a batch of operations as quickly as possible.
    
    Args:
        operations (list): List of operation tuples in the format:
                          ('key_down', key) or ('key_up', key) or
                          ('mouse_down', button) or ('mouse_up', button)
    
    Returns:
        bool: True if all operations were successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Windows API implementation - no batch capability, execute sequentially
        for op_type, arg in operations:
            if op_type == 'key_down':
                if not key_down_windows_api(arg):
                    return False
            elif op_type == 'key_up':
                if not key_up_windows_api(arg):
                    return False
            elif op_type == 'mouse_down':
                if not mouse_button_down_windows_api(arg):
                    return False
            elif op_type == 'mouse_up':
                if not mouse_button_up_windows_api(arg):
                    return False
        
        return True
    
    if not initialized:
        if not initialize():
            # Fallback to Windows API
            return send_batch_operations_windows_api(operations)
    
    try:
        # Interception implementation - execute as fast as possible
        for op_type, arg in operations:
            if op_type == 'key_down':
                interception.key_down(arg)
            elif op_type == 'key_up':
                interception.key_up(arg)
            elif op_type == 'mouse_down':
                interception.mouse_down(arg)
            elif op_type == 'mouse_up':
                interception.mouse_up(arg)
        
        return True
    except Exception as e:
        print(f"Error sending batch operations with Interception: {e}")
        # Fallback to Windows API
        for op_type, arg in operations:
            if op_type == 'key_down':
                if not key_down_windows_api(arg):
                    return False
            elif op_type == 'key_up':
                if not key_up_windows_api(arg):
                    return False
            elif op_type == 'mouse_down':
                if not mouse_button_down_windows_api(arg):
                    return False
            elif op_type == 'mouse_up':
                if not mouse_button_up_windows_api(arg):
                    return False
        
        return True

# Initialize the Interception context when the module is imported
initialize()

# Clean up when the module is unloaded
import atexit
atexit.register(cleanup)

# Test function
if __name__ == "__main__":
    print("Testing optimized input module...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Type "Hello, World!"
    for char in "Hello, World!":
        press_key(char.lower())
        time.sleep(0.1)
    
    print("Test complete.")
