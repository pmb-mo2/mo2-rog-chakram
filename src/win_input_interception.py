"""
Windows input module using interception-python for direct key simulation.
This module uses the Interception driver to capture and simulate keyboard and mouse input.
If the Interception driver is not available, it falls back to using the Windows API.
"""

import time
import ctypes
import sys
import os

# Try to import interception-python, but handle the case where it's not available
# or the driver is not properly installed
INTERCEPTION_AVAILABLE = False
try:
    import interception
    INTERCEPTION_AVAILABLE = True
except (ImportError, Exception) as e:
    print(f"Warning: Could not initialize Interception driver: {e}")
    print("Falling back to Windows API for input simulation.")

# Virtual key codes
VK_CODES = {
    # Arrow keys
    'left': 0x25,    # VK_LEFT
    'up': 0x26,      # VK_UP
    'right': 0x27,   # VK_RIGHT
    'down': 0x28,    # VK_DOWN
    
    # Number keys
    '0': 0x30,       # 0 key
    '1': 0x31,       # 1 key
    '2': 0x32,       # 2 key
    '3': 0x33,       # 3 key
    '4': 0x34,       # 4 key
    '5': 0x35,       # 5 key
    '6': 0x36,       # 6 key
    '7': 0x37,       # 7 key
    '8': 0x38,       # 8 key
    '9': 0x39,       # 9 key
    
    # Letter keys
    'a': 0x41,       # A key
    'b': 0x42,       # B key
    'c': 0x43,       # C key
    'd': 0x44,       # D key
    'e': 0x45,       # E key
    'f': 0x46,       # F key
    'g': 0x47,       # G key
    'h': 0x48,       # H key
    'i': 0x49,       # I key
    'j': 0x4A,       # J key
    'k': 0x4B,       # K key
    'l': 0x4C,       # L key
    'm': 0x4D,       # M key
    'n': 0x4E,       # N key
    'o': 0x4F,       # O key
    'p': 0x50,       # P key
    'q': 0x51,       # Q key
    'r': 0x52,       # R key
    's': 0x53,       # S key
    't': 0x54,       # T key
    'u': 0x55,       # U key
    'v': 0x56,       # V key
    'w': 0x57,       # W key
    'x': 0x58,       # X key
    'y': 0x59,       # Y key
    'z': 0x5A,       # Z key
    
    # Function keys
    'f1': 0x70,      # F1 key
    'f2': 0x71,      # F2 key
    'f3': 0x72,      # F3 key
    'f4': 0x73,      # F4 key
    'f5': 0x74,      # F5 key
    'f6': 0x75,      # F6 key
    'f7': 0x76,      # F7 key
    'f8': 0x77,      # F8 key
    'f9': 0x78,      # F9 key
    'f10': 0x79,     # F10 key
    'f11': 0x7A,     # F11 key
    'f12': 0x7B,     # F12 key
    
    # Other keys
    'esc': 0x1B,     # ESC key
    'tab': 0x09,     # TAB key
    'shift': 0x10,   # SHIFT key
    'ctrl': 0x11,    # CTRL key
    'alt': 0x12,     # ALT key
    'space': 0x20,   # SPACEBAR
    'enter': 0x0D,   # ENTER key
    'backspace': 0x08, # BACKSPACE key
    'delete': 0x2E,  # DELETE key
    'home': 0x24,    # HOME key
    'end': 0x23,     # END key
    'pageup': 0x21,  # PAGE UP key
    'pagedown': 0x22 # PAGE DOWN key
}

# Scan codes (used by Interception)
SCAN_CODES = {
    # Arrow keys
    'left': 0xE04B,   # Left arrow
    'up': 0xE048,     # Up arrow
    'right': 0xE04D,  # Right arrow
    'down': 0xE050,   # Down arrow
    
    # Number keys
    '0': 0x0B,        # 0 key
    '1': 0x02,        # 1 key
    '2': 0x03,        # 2 key
    '3': 0x04,        # 3 key
    '4': 0x05,        # 4 key
    '5': 0x06,        # 5 key
    '6': 0x07,        # 6 key
    '7': 0x08,        # 7 key
    '8': 0x09,        # 8 key
    '9': 0x0A,        # 9 key
    
    # Letter keys
    'a': 0x1E,        # A key
    'b': 0x30,        # B key
    'c': 0x2E,        # C key
    'd': 0x20,        # D key
    'e': 0x12,        # E key
    'f': 0x21,        # F key
    'g': 0x22,        # G key
    'h': 0x23,        # H key
    'i': 0x17,        # I key
    'j': 0x24,        # J key
    'k': 0x25,        # K key
    'l': 0x26,        # L key
    'm': 0x32,        # M key
    'n': 0x31,        # N key
    'o': 0x18,        # O key
    'p': 0x19,        # P key
    'q': 0x10,        # Q key
    'r': 0x13,        # R key
    's': 0x1F,        # S key
    't': 0x14,        # T key
    'u': 0x16,        # U key
    'v': 0x2F,        # V key
    'w': 0x11,        # W key
    'x': 0x2D,        # X key
    'y': 0x15,        # Y key
    'z': 0x2C,        # Z key
    
    # Function keys
    'f1': 0x3B,       # F1 key
    'f2': 0x3C,       # F2 key
    'f3': 0x3D,       # F3 key
    'f4': 0x3E,       # F4 key
    'f5': 0x3F,       # F5 key
    'f6': 0x40,       # F6 key
    'f7': 0x41,       # F7 key
    'f8': 0x42,       # F8 key
    'f9': 0x43,       # F9 key
    'f10': 0x44,      # F10 key
    'f11': 0x57,      # F11 key
    'f12': 0x58,      # F12 key
    
    # Other keys
    'esc': 0x01,      # ESC key
    'tab': 0x0F,      # TAB key
    'shift': 0x2A,    # Left SHIFT key
    'ctrl': 0x1D,     # Left CTRL key
    'alt': 0x38,      # Left ALT key
    'space': 0x39,    # SPACEBAR
    'enter': 0x1C,    # ENTER key
    'backspace': 0x0E, # BACKSPACE key
    'delete': 0xE053, # DELETE key
    'home': 0xE047,   # HOME key
    'end': 0xE04F,    # END key
    'pageup': 0xE049, # PAGE UP key
    'pagedown': 0xE051 # PAGE DOWN key
}

# Constants for SendInput (Windows API fallback)
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

# Define input structures for Windows API fallback
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION)
    ]

# Load user32.dll for Windows API fallback
user32 = ctypes.WinDLL('user32', use_last_error=True)

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

def key_down_windows_api(key):
    """
    Send a key down event using the Windows API.
    
    Args:
        key (str): The key to press (must be in VK_CODES)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if key not in VK_CODES:
        print(f"Error: Key '{key}' not found in VK_CODES")
        return False
    
    try:
        # Create a keyboard input
        inputs = (INPUT * 1)()
        inputs[0].type = 1  # INPUT_KEYBOARD
        inputs[0].union.ki.wVk = VK_CODES[key]
        inputs[0].union.ki.wScan = 0
        inputs[0].union.ki.dwFlags = KEYEVENTF_KEYDOWN
        inputs[0].union.ki.time = 0
        inputs[0].union.ki.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending key down event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending key down event: {e}")
        return False

def key_down(key):
    """
    Send a key down event using Interception or Windows API fallback.
    
    Args:
        key (str): The key to press (must be in SCAN_CODES/VK_CODES)
    
    Returns:
        bool: True if successful, False otherwise
    """
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

def key_up_windows_api(key):
    """
    Send a key up event using the Windows API.
    
    Args:
        key (str): The key to release (must be in VK_CODES)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if key not in VK_CODES:
        print(f"Error: Key '{key}' not found in VK_CODES")
        return False
    
    try:
        # Create a keyboard input
        inputs = (INPUT * 1)()
        inputs[0].type = 1  # INPUT_KEYBOARD
        inputs[0].union.ki.wVk = VK_CODES[key]
        inputs[0].union.ki.wScan = 0
        inputs[0].union.ki.dwFlags = KEYEVENTF_KEYUP
        inputs[0].union.ki.time = 0
        inputs[0].union.ki.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending key up event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending key up event: {e}")
        return False

def key_up(key):
    """
    Send a key up event using Interception or Windows API fallback.
    
    Args:
        key (str): The key to release (must be in SCAN_CODES/VK_CODES)
    
    Returns:
        bool: True if successful, False otherwise
    """
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
    """
    Press and release a key as a single atomic operation.
    
    Args:
        key (str): The key to press and release
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Press and release the key using Windows API
        if not key_down(key):
            return False
        
        # No delay for maximum responsiveness
        
        if not key_up(key):
            return False
        
        return True
    
    try:
        # Use the interception press function
        interception.press(key)
        return True
    except Exception as e:
        print(f"Error pressing key with Interception: {e}")
        print("Falling back to Windows API...")
        
        # Fallback to Windows API
        if not key_down_windows_api(key):
            return False
        
        # No delay for maximum responsiveness
        
        if not key_up_windows_api(key):
            return False
        
        return True

def send_key_sequence_windows_api(keys, delay=0.01):
    """
    Send a sequence of key events with precise timing using Windows API.
    
    Args:
        keys (list): List of (key, is_up) tuples
        delay (float): Delay between key events. If 0, all events are sent atomically.
    
    Returns:
        bool: True if all events were sent successfully, False otherwise
    """
    # If no delay is needed, send all inputs atomically
    if delay <= 0:
        try:
            # Create an array of inputs
            inputs = (INPUT * len(keys))()
            
            for i, (key, is_up) in enumerate(keys):
                if key not in VK_CODES:
                    print(f"Error: Key '{key}' not found in VK_CODES")
                    continue
                
                # Create a keyboard input
                inputs[i].type = 1  # INPUT_KEYBOARD
                inputs[i].union.ki.wVk = VK_CODES[key]
                inputs[i].union.ki.wScan = 0
                inputs[i].union.ki.dwFlags = KEYEVENTF_KEYUP if is_up else KEYEVENTF_KEYDOWN
                inputs[i].union.ki.time = 0
                inputs[i].union.ki.dwExtraInfo = None
            
            # Send all inputs
            result = user32.SendInput(len(keys), inputs, ctypes.sizeof(INPUT))
            
            if result != len(keys):
                error = ctypes.get_last_error()
                print(f"Error sending key sequence: {error}")
                return False
            
            return True
        except Exception as e:
            print(f"Error sending key sequence: {e}")
            return False
    
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
        return send_key_sequence_windows_api(keys, delay)
    
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
        return send_key_sequence_windows_api(keys, delay)

def middle_mouse_down_windows_api():
    """
    Send a middle mouse button down event using Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a mouse input
        inputs = (INPUT * 1)()
        inputs[0].type = 0  # INPUT_MOUSE
        inputs[0].union.mi.dx = 0
        inputs[0].union.mi.dy = 0
        inputs[0].union.mi.mouseData = 0
        inputs[0].union.mi.dwFlags = MOUSEEVENTF_MIDDLEDOWN
        inputs[0].union.mi.time = 0
        inputs[0].union.mi.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending middle mouse down event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending middle mouse down event: {e}")
        return False

def middle_mouse_down():
    """
    Send a middle mouse button down event using Interception or Windows API fallback.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return middle_mouse_down_windows_api()
    
    global mouse
    
    if not mouse:
        if not initialize():
            return middle_mouse_down_windows_api()
    
    try:
        # Use the interception mouse_down function with middle button
        interception.mouse_down('middle')
        return True
    except Exception as e:
        print(f"Error sending middle mouse down event with Interception: {e}")
        print("Falling back to Windows API...")
        return middle_mouse_down_windows_api()

def middle_mouse_up_windows_api():
    """
    Send a middle mouse button up event using Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a mouse input
        inputs = (INPUT * 1)()
        inputs[0].type = 0  # INPUT_MOUSE
        inputs[0].union.mi.dx = 0
        inputs[0].union.mi.dy = 0
        inputs[0].union.mi.mouseData = 0
        inputs[0].union.mi.dwFlags = MOUSEEVENTF_MIDDLEUP
        inputs[0].union.mi.time = 0
        inputs[0].union.mi.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending middle mouse up event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending middle mouse up event: {e}")
        return False

def middle_mouse_up():
    """
    Send a middle mouse button up event using Interception or Windows API fallback.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return middle_mouse_up_windows_api()
    
    global mouse
    
    if not mouse:
        if not initialize():
            return middle_mouse_up_windows_api()
    
    try:
        # Use the interception mouse_up function with middle button
        interception.mouse_up('middle')
        return True
    except Exception as e:
        print(f"Error sending middle mouse up event with Interception: {e}")
        print("Falling back to Windows API...")
        return middle_mouse_up_windows_api()

def click_middle_mouse():
    """
    Click the middle mouse button (press and release).
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Press and release the middle mouse button using Windows API
        if not middle_mouse_down_windows_api():
            return False
        
        # No delay for maximum responsiveness
        
        if not middle_mouse_up_windows_api():
            return False
        
        return True
    
    try:
        # Use the interception click function with middle button
        interception.click('middle')
        return True
    except Exception as e:
        print(f"Error clicking middle mouse with Interception: {e}")
        print("Falling back to Windows API...")
        
        # Fallback to Windows API
        if not middle_mouse_down_windows_api():
            return False
        
        # No delay for maximum responsiveness
        
        if not middle_mouse_up_windows_api():
            return False
        
        return True

def left_mouse_down_windows_api():
    """
    Send a left mouse button down event using Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a mouse input
        inputs = (INPUT * 1)()
        inputs[0].type = 0  # INPUT_MOUSE
        inputs[0].union.mi.dx = 0
        inputs[0].union.mi.dy = 0
        inputs[0].union.mi.mouseData = 0
        inputs[0].union.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
        inputs[0].union.mi.time = 0
        inputs[0].union.mi.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending left mouse down event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending left mouse down event: {e}")
        return False

def left_mouse_down():
    """
    Send a left mouse button down event using Interception or Windows API fallback.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return left_mouse_down_windows_api()
    
    global mouse
    
    if not mouse:
        if not initialize():
            return left_mouse_down_windows_api()
    
    try:
        # Use the interception mouse_down function with left button
        interception.mouse_down('left')
        return True
    except Exception as e:
        print(f"Error sending left mouse down event with Interception: {e}")
        print("Falling back to Windows API...")
        return left_mouse_down_windows_api()

def left_mouse_up_windows_api():
    """
    Send a left mouse button up event using Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a mouse input
        inputs = (INPUT * 1)()
        inputs[0].type = 0  # INPUT_MOUSE
        inputs[0].union.mi.dx = 0
        inputs[0].union.mi.dy = 0
        inputs[0].union.mi.mouseData = 0
        inputs[0].union.mi.dwFlags = MOUSEEVENTF_LEFTUP
        inputs[0].union.mi.time = 0
        inputs[0].union.mi.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending left mouse up event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending left mouse up event: {e}")
        return False

def left_mouse_up():
    """
    Send a left mouse button up event using Interception or Windows API fallback.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return left_mouse_up_windows_api()
    
    global mouse
    
    if not mouse:
        if not initialize():
            return left_mouse_up_windows_api()
    
    try:
        # Use the interception mouse_up function with left button
        interception.mouse_up('left')
        return True
    except Exception as e:
        print(f"Error sending left mouse up event with Interception: {e}")
        print("Falling back to Windows API...")
        return left_mouse_up_windows_api()

def click_left_mouse():
    """
    Click the left mouse button (press and release).
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Press and release the left mouse button using Windows API
        if not left_mouse_down_windows_api():
            return False
        
        # No delay for maximum responsiveness
        
        if not left_mouse_up_windows_api():
            return False
        
        return True
    
    try:
        # Use the interception left_click function
        interception.left_click()
        return True
    except Exception as e:
        print(f"Error clicking left mouse with Interception: {e}")
        print("Falling back to Windows API...")
        
        # Fallback to Windows API
        if not left_mouse_down_windows_api():
            return False
        
        # No delay for maximum responsiveness
        
        if not left_mouse_up_windows_api():
            return False
        
        return True

def right_mouse_down_windows_api():
    """
    Send a right mouse button down event using Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a mouse input
        inputs = (INPUT * 1)()
        inputs[0].type = 0  # INPUT_MOUSE
        inputs[0].union.mi.dx = 0
        inputs[0].union.mi.dy = 0
        inputs[0].union.mi.mouseData = 0
        inputs[0].union.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN
        inputs[0].union.mi.time = 0
        inputs[0].union.mi.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending right mouse down event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending right mouse down event: {e}")
        return False

def right_mouse_down():
    """
    Send a right mouse button down event using Interception or Windows API fallback.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return right_mouse_down_windows_api()
    
    global mouse
    
    if not mouse:
        if not initialize():
            return right_mouse_down_windows_api()
    
    try:
        # Use the interception mouse_down function with right button
        interception.mouse_down('right')
        return True
    except Exception as e:
        print(f"Error sending right mouse down event with Interception: {e}")
        print("Falling back to Windows API...")
        return right_mouse_down_windows_api()

def right_mouse_up_windows_api():
    """
    Send a right mouse button up event using Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a mouse input
        inputs = (INPUT * 1)()
        inputs[0].type = 0  # INPUT_MOUSE
        inputs[0].union.mi.dx = 0
        inputs[0].union.mi.dy = 0
        inputs[0].union.mi.mouseData = 0
        inputs[0].union.mi.dwFlags = MOUSEEVENTF_RIGHTUP
        inputs[0].union.mi.time = 0
        inputs[0].union.mi.dwExtraInfo = None
        
        # Send the input
        result = user32.SendInput(1, inputs, ctypes.sizeof(INPUT))
        
        if result != 1:
            error = ctypes.get_last_error()
            print(f"Error sending right mouse up event: {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Error sending right mouse up event: {e}")
        return False

def right_mouse_up():
    """
    Send a right mouse button up event using Interception or Windows API fallback.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return right_mouse_up_windows_api()
    
    global mouse
    
    if not mouse:
        if not initialize():
            return right_mouse_up_windows_api()
    
    try:
        # Use the interception mouse_up function with right button
        interception.mouse_up('right')
        return True
    except Exception as e:
        print(f"Error sending right mouse up event with Interception: {e}")
        print("Falling back to Windows API...")
        return right_mouse_up_windows_api()

def click_right_mouse():
    """
    Click the right mouse button (press and release).
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        # Press and release the right mouse button using Windows API
        if not right_mouse_down_windows_api():
            return False
        
        # No delay for maximum responsiveness
        
        if not right_mouse_up_windows_api():
            return False
        
        return True
    
    try:
        # Use the interception right_click function
        interception.right_click()
        return True
    except Exception as e:
        print(f"Error clicking right mouse with Interception: {e}")
        print("Falling back to Windows API...")
        
        # Fallback to Windows API
        if not right_mouse_down_windows_api():
            return False
        
        # No delay for maximum responsiveness
        
        if not right_mouse_up_windows_api():
            return False
        
        return True

def send_sector_change_windows_api(cancel_key, old_attack_key, new_attack_key):
    """
    Send a precise sector change sequence using Windows API.
    
    Args:
        cancel_key (str): The cancel key or "middle_mouse" for middle mouse button
        old_attack_key (str): The old attack key
        new_attack_key (str): The new attack key
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if we're using the middle mouse button for cancel
        if cancel_key == "middle_mouse":
            # Use middle mouse button
            if not middle_mouse_down_windows_api():
                return False
            
            if not key_up_windows_api(old_attack_key):
                return False
            
            if not middle_mouse_up_windows_api():
                return False
            
            if not key_down_windows_api(new_attack_key):
                return False
        else:
            # Use keyboard key for cancel
            if not key_down_windows_api(cancel_key):
                return False
            
            if not key_up_windows_api(old_attack_key):
                return False
            
            if not key_up_windows_api(cancel_key):
                return False
            
            if not key_down_windows_api(new_attack_key):
                return False
        
        return True
    except Exception as e:
        print(f"Error sending sector change with Windows API: {e}")
        return False

def send_sector_change(cancel_key, old_attack_key, new_attack_key, release_delay=0.0):
    """
    Send a precise sector change sequence as a single atomic operation for maximum speed.
    All key events are sent in a single batch to minimize latency.
    
    If cancel_key is "middle_mouse", it will use the middle mouse button instead of a keyboard key.
    
    Args:
        cancel_key (str): The cancel key or "middle_mouse" for middle mouse button
        old_attack_key (str): The old attack key
        new_attack_key (str): The new attack key
        release_delay (float): Not used anymore, kept for compatibility
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not INTERCEPTION_AVAILABLE:
        return send_sector_change_windows_api(cancel_key, old_attack_key, new_attack_key)
    
    global keyboard, mouse
    
    if not keyboard or not mouse:
        if not initialize():
            return send_sector_change_windows_api(cancel_key, old_attack_key, new_attack_key)
    
    try:
        # Check if we're using the middle mouse button for cancel
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
        print("Falling back to Windows API...")
        return send_sector_change_windows_api(cancel_key, old_attack_key, new_attack_key)

# Initialize Interception when the module is imported
initialize()

# Clean up Interception when the module is unloaded
import atexit
atexit.register(cleanup)

# Test function
if __name__ == "__main__":
    print("Testing Interception input module...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Type "Hello, World!"
    for char in "Hello, World!":
        press_key(char.lower())
        time.sleep(0.1)
    
    print("Test complete.")
