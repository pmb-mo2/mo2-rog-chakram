"""
Windows input module using interception-python for direct key simulation.
This module uses the Interception driver to capture and simulate keyboard and mouse input.
If the Interception driver is not available, it falls back to using the Windows API.
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
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

# Virtual key codes (for Windows API fallback)
VK_CODES = {
    'left': 0x25,  # VK_LEFT
    'up': 0x26,    # VK_UP
    'right': 0x27, # VK_RIGHT
    'down': 0x28,  # VK_DOWN
    'c': 0x43,     # C key
    'esc': 0x1B,   # ESC key
    'alt': 0x12,   # VK_MENU (Alt key)
    # Add more keys as needed
}

# Scan codes (used by Interception)
SCAN_CODES = {
    'left': 0xE04B,   # Left arrow
    'up': 0xE048,     # Up arrow
    'right': 0xE04D,  # Right arrow
    'down': 0xE050,   # Down arrow
    'c': 0x2E,        # C key
    'esc': 0x01,      # ESC key
    'alt': 0x38,      # Left Alt key
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

# Get cursor position function
GetCursorPos = user32.GetCursorPos
GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
GetCursorPos.restype = wintypes.BOOL

# Initialize Interception devices
keyboard = None
mouse = None

def initialize():
    """Initialize the Interception devices or fallback to Windows API."""
    global keyboard, mouse
    
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
        
        return True
    except Exception as e:
        print(f"Error initializing Interception: {e}")
        return False

def cleanup():
    """Clean up the Interception resources."""
    # No explicit cleanup needed for the new API
    pass

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

def create_mouse_move_input(dx, dy, absolute=False):
    """Create an INPUT structure for a mouse movement event (Windows API)."""
    flags = MOUSEEVENTF_MOVE
    if absolute:
        flags |= MOUSEEVENTF_ABSOLUTE
    
    return INPUT(
        type=INPUT_MOUSE,
        union=INPUT_UNION(
            mi=MOUSEINPUT(
                dx=dx,
                dy=dy,
                mouseData=0,
                dwFlags=flags,
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

def move_mouse_windows_api(dx, dy, absolute=False):
    """Move the mouse cursor by the specified delta using Windows API."""
    try:
        input_struct = create_mouse_move_input(dx, dy, absolute)
        
        result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error moving mouse cursor: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error moving mouse cursor: {e}")
        return False

def get_cursor_position():
    """Get the current cursor position."""
    point = wintypes.POINT()
    if not GetCursorPos(ctypes.byref(point)):
        error = ctypes.get_last_error()
        print(f"Error getting cursor position: {error}")
        return (0, 0)
    
    return (point.x, point.y)

def is_key_pressed(key):
    """Check if a key is currently pressed."""
    if not INTERCEPTION_AVAILABLE:
        # Use Windows API to check key state
        try:
            if key not in VK_CODES:
                print(f"Error: Key '{key}' not found in VK_CODES")
                return False
            
            # Import GetAsyncKeyState function
            GetAsyncKeyState = user32.GetAsyncKeyState
            GetAsyncKeyState.argtypes = [wintypes.INT]
            GetAsyncKeyState.restype = wintypes.SHORT
            
            # Check if key is pressed (highest bit is set)
            key_state = GetAsyncKeyState(VK_CODES[key])
            return (key_state & 0x8000) != 0
        except Exception as e:
            print(f"Error checking key state: {e}")
            return False
    else:
        try:
            # For Interception, we can't directly check key state
            # This is a limitation of the Interception API
            # Fallback to Windows API
            if key not in VK_CODES:
                print(f"Error: Key '{key}' not found in VK_CODES")
                return False
            
            # Import GetAsyncKeyState function
            GetAsyncKeyState = user32.GetAsyncKeyState
            GetAsyncKeyState.argtypes = [wintypes.INT]
            GetAsyncKeyState.restype = wintypes.SHORT
            
            # Check if key is pressed (highest bit is set)
            key_state = GetAsyncKeyState(VK_CODES[key])
            return (key_state & 0x8000) != 0
        except Exception as e:
            print(f"Error checking key state with Interception: {e}")
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
    
    global keyboard
    
    if not keyboard:
        if not initialize():
            return key_down_windows_api(key)
    
    try:
        # Use the interception key_down function
        interception.key_down(key)
        return True
    except Exception as e:
        print(f"Error sending key down event with Interception: {e}")
        print("Falling back to Windows API...")
        return key_down_windows_api(key)

def key_up(key):
    """Send a key up event using Interception or Windows API fallback."""
    if not INTERCEPTION_AVAILABLE:
        return key_up_windows_api(key)
    
    global keyboard
    
    if not keyboard:
        if not initialize():
            return key_up_windows_api(key)
    
    try:
        # Use the interception key_up function
        interception.key_up(key)
        return True
    except Exception as e:
        print(f"Error sending key up event with Interception: {e}")
        print("Falling back to Windows API...")
        return key_up_windows_api(key)

def press_key(key):
    """Press and release a key as a single atomic operation."""
    if not key_down(key):
        return False
    
    # No delay for maximum responsiveness
    
    if not key_up(key):
        return False
    
    return True

def left_mouse_down():
    """Send a left mouse button down event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_down_windows_api('left')
    
    global mouse
    
    if not mouse:
        if not initialize():
            return mouse_button_down_windows_api('left')
    
    try:
        # Use the interception mouse_down function with left button
        interception.mouse_down('left')
        return True
    except Exception as e:
        print(f"Error sending left mouse down event with Interception: {e}")
        print("Falling back to Windows API...")
        return mouse_button_down_windows_api('left')

def right_mouse_down():
    """Send a right mouse button down event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_down_windows_api('right')
    
    global mouse
    
    if not mouse:
        if not initialize():
            return mouse_button_down_windows_api('right')
    
    try:
        # Use the interception mouse_down function with right button
        interception.mouse_down('right')
        return True
    except Exception as e:
        print(f"Error sending right mouse down event with Interception: {e}")
        print("Falling back to Windows API...")
        return mouse_button_down_windows_api('right')

def right_mouse_up():
    """Send a right mouse button up event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_up_windows_api('right')
    
    global mouse
    
    if not mouse:
        if not initialize():
            return mouse_button_up_windows_api('right')
    
    try:
        # Use the interception mouse_up function with right button
        interception.mouse_up('right')
        return True
    except Exception as e:
        print(f"Error sending right mouse up event with Interception: {e}")
        print("Falling back to Windows API...")
        return mouse_button_up_windows_api('right')

def move_mouse(dx, dy):
    """Move the mouse cursor by the specified delta."""
    # Always use Windows API for mouse movement as Interception doesn't support it directly
    return move_mouse_windows_api(dx, dy)

def left_mouse_up():
    """Send a left mouse button up event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_up_windows_api('left')
    
    global mouse
    
    if not mouse:
        if not initialize():
            return mouse_button_up_windows_api('left')
    
    try:
        # Use the interception mouse_up function with left button
        interception.mouse_up('left')
        return True
    except Exception as e:
        print(f"Error sending left mouse up event with Interception: {e}")
        print("Falling back to Windows API...")
        return mouse_button_up_windows_api('left')

def click_left_mouse():
    """Click the left mouse button (press and release)."""
    if not left_mouse_down():
        return False
    
    # No delay for maximum responsiveness
    
    if not left_mouse_up():
        return False
    
    return True

def middle_mouse_down():
    """Send a middle mouse button down event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_down_windows_api('middle')
    
    global mouse
    
    if not mouse:
        if not initialize():
            return mouse_button_down_windows_api('middle')
    
    try:
        # Use the interception mouse_down function with middle button
        interception.mouse_down('middle')
        return True
    except Exception as e:
        print(f"Error sending middle mouse down event with Interception: {e}")
        print("Falling back to Windows API...")
        return mouse_button_down_windows_api('middle')

def middle_mouse_up():
    """Send a middle mouse button up event."""
    if not INTERCEPTION_AVAILABLE:
        return mouse_button_up_windows_api('middle')
    
    global mouse
    
    if not mouse:
        if not initialize():
            return mouse_button_up_windows_api('middle')
    
    try:
        # Use the interception mouse_up function with middle button
        interception.mouse_up('middle')
        return True
    except Exception as e:
        print(f"Error sending middle mouse up event with Interception: {e}")
        print("Falling back to Windows API...")
        return mouse_button_up_windows_api('middle')

def click_middle_mouse():
    """Click the middle mouse button (press and release)."""
    if not middle_mouse_down():
        return False
    
    # No delay for maximum responsiveness
    
    if not middle_mouse_up():
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
        try:
            # If no delay is needed, send all inputs atomically
            if delay <= 0:
                # Create an array of inputs
                inputs = (ctypes.POINTER(INPUT) * len(keys))()
                
                for i, (key, is_up) in enumerate(keys):
                    if key not in VK_CODES:
                        print(f"Error: Key '{key}' not found in VK_CODES")
                        continue
                    
                    # Create a keyboard input
                    input_struct = INPUT(
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
                    
                    inputs[i] = ctypes.pointer(input_struct)
                
                # Send all inputs
                result = SendInput(len(keys), inputs, ctypes.sizeof(INPUT))
                
                if result != len(keys):
                    error = ctypes.get_last_error()
                    print(f"Error sending key sequence: {error}")
                    return False
                
                return True
            
            # If delay is needed, send inputs one by one with the specified delay
            for key, is_up in keys:
                if is_up:
                    if not key_up_windows_api(key):
                        return False
                else:
                    if not key_down_windows_api(key):
                        return False
                
                time.sleep(delay)
            
            return True
        except Exception as e:
            print(f"Error sending key sequence: {e}")
            return False
    else:
        global keyboard
        
        if not keyboard:
            if not initialize():
                return send_key_sequence_windows_api(keys, delay)
        
        try:
            # Send inputs one by one with the specified delay
            for key, is_up in keys:
                if is_up:
                    interception.key_up(key)
                else:
                    interception.key_down(key)
                
                if delay > 0:
                    time.sleep(delay)
            
            return True
        except Exception as e:
            print(f"Error sending key sequence with Interception: {e}")
            print("Falling back to Windows API...")
            
            # If delay is needed, send inputs one by one with the specified delay
            for key, is_up in keys:
                if is_up:
                    if not key_up_windows_api(key):
                        return False
                else:
                    if not key_down_windows_api(key):
                        return False
                
                time.sleep(delay)
            
            return True

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
    print(f"Executing sector change: {old_attack_key} -> {new_attack_key} with cancel: {cancel_key}")
    
    if not INTERCEPTION_AVAILABLE:
        # Check if we're using the middle mouse button for cancel
        if cancel_key == "middle_mouse":
            # 1. Press middle mouse button
            if not middle_mouse_down():
                print("Failed to press middle mouse button")
                return False
            
            # Small delay to ensure cancel is registered
            time.sleep(0.01)
            
            # 2. Release old attack key
            if not key_up(old_attack_key):
                print(f"Failed to release old attack key: {old_attack_key}")
                return False
            
            # 3. Release middle mouse button
            if not middle_mouse_up():
                print("Failed to release middle mouse button")
                return False
        else:
            # 1. Press cancel key
            if not key_down(cancel_key):
                print(f"Failed to press cancel key: {cancel_key}")
                return False
            
            # Small delay to ensure cancel is registered
            time.sleep(0.01)
            
            # 2. Release old attack key
            if not key_up(old_attack_key):
                print(f"Failed to release old attack key: {old_attack_key}")
                return False
            
            # 3. Release cancel key
            if not key_up(cancel_key):
                print(f"Failed to release cancel key: {cancel_key}")
                return False
        
        # Small delay before pressing new attack key
        time.sleep(0.01)
        
        # 4. Press new attack key
        if not key_down(new_attack_key):
            print(f"Failed to press new attack key: {new_attack_key}")
            return False
        
        print(f"Sector change completed: {old_attack_key} -> {new_attack_key}")
        return True
    else:
        global keyboard, mouse
        
        if not keyboard or not mouse:
            if not initialize():
                # Fallback to Windows API implementation
                return send_sector_change(cancel_key, old_attack_key, new_attack_key, release_delay)
        
        try:
            # Check if we're using the middle mouse button for cancel
            if cancel_key == "middle_mouse":
                # Use middle mouse button
                print("Using middle mouse button for cancel")
                interception.mouse_down('middle')
                time.sleep(0.01)  # Small delay to ensure cancel is registered
                interception.key_up(old_attack_key)
                interception.mouse_up('middle')
                time.sleep(0.01)  # Small delay before pressing new attack key
                interception.key_down(new_attack_key)
            else:
                # Use keyboard key for cancel
                print(f"Using keyboard key for cancel: {cancel_key}")
                interception.key_down(cancel_key)
                time.sleep(0.01)  # Small delay to ensure cancel is registered
                interception.key_up(old_attack_key)
                interception.key_up(cancel_key)
                time.sleep(0.01)  # Small delay before pressing new attack key
                interception.key_down(new_attack_key)
            
            print(f"Sector change completed with Interception: {old_attack_key} -> {new_attack_key}")
            return True
        except Exception as e:
            print(f"Error sending sector change with Interception: {e}")
            print("Falling back to Windows API...")
            
            # Fallback to Windows API implementation
            return send_sector_change(cancel_key, old_attack_key, new_attack_key, release_delay)

# Initialize the Interception context when the module is imported
initialize()

# Clean up when the module is unloaded
import atexit
atexit.register(cleanup)

# Test function
if __name__ == "__main__":
    print("Testing input module...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Type "Hello, World!"
    for char in "Hello, World!":
        press_key(char.lower())
        time.sleep(0.1)
    
    print("Test complete.")
