"""
Windows API input module for direct key simulation.
This module uses ctypes to directly interface with the Windows API for sending input events.
"""

import ctypes
import time
from ctypes import wintypes

# Windows API constants
INPUT_KEYBOARD = 1
INPUT_MOUSE = 0
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# Mouse constants
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

# Virtual key codes
VK_CODES = {
    'left': 0x25,  # VK_LEFT
    'up': 0x26,    # VK_UP
    'right': 0x27, # VK_RIGHT
    'down': 0x28,  # VK_DOWN
    'c': 0x43,     # C key
    'esc': 0x1B,   # ESC key
    # Add more keys as needed
}

# Define input structures
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

# Load user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Define SendInput function
SendInput = user32.SendInput
SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), wintypes.INT)
SendInput.restype = wintypes.UINT

def key_down(key):
    """
    Send a key down event using the Windows API.
    Optimized for maximum speed using direct input creation.
    
    Args:
        key (str): The key to press (must be in VK_CODES)
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create key down input
    input_struct = create_key_input(key, False)
    if not input_struct:
        return False
    
    # Send input directly
    result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
    
    if result != 1:
        error = ctypes.get_last_error()
        print(f"Error sending key down event: {error}")
        return False
    
    return True

def key_up(key):
    """
    Send a key up event using the Windows API.
    Optimized for maximum speed using direct input creation.
    
    Args:
        key (str): The key to release (must be in VK_CODES)
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create key up input
    input_struct = create_key_input(key, True)
    if not input_struct:
        return False
    
    # Send input directly
    result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
    
    if result != 1:
        error = ctypes.get_last_error()
        print(f"Error sending key up event: {error}")
        return False
    
    return True

def press_key(key):
    """
    Press and release a key as a single atomic operation for maximum speed.
    Both key down and key up events are sent in a single Windows API call.
    
    Args:
        key (str): The key to press and release
    
    Returns:
        bool: True if successful, False otherwise
    """
    if key not in VK_CODES:
        print(f"Error: Key '{key}' not found in VK_CODES")
        return False
    
    # Create both key down and key up inputs
    inputs = []
    inputs.append(create_key_input(key, False))  # Key down
    inputs.append(create_key_input(key, True))   # Key up
    
    # Remove any None values (shouldn't happen but just in case)
    inputs = [inp for inp in inputs if inp is not None]
    
    # Send all inputs in a single atomic operation
    if inputs:
        # Create an array of INPUT structures
        input_array = (INPUT * len(inputs))(*inputs)
        
        # Send the inputs directly
        result = SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
        
        if result != len(inputs):
            error = ctypes.get_last_error()
            print(f"Error sending press key inputs: {error}")
            return False
    
    return True

def send_key_sequence(keys, delay=0.01):
    """
    Send a sequence of key events with precise timing.
    If delay is 0, all events are sent as a single atomic operation for maximum speed.
    
    Args:
        keys (list): List of (key, is_up) tuples
        delay (float): Delay between key events. If 0, all events are sent atomically.
    
    Returns:
        bool: True if all events were sent successfully, False otherwise
    """
    # If no delay is needed, send all inputs atomically
    if delay <= 0:
        inputs = []
        for key, is_up in keys:
            input_struct = create_key_input(key, is_up)
            if input_struct:
                inputs.append(input_struct)
        
        # Send all inputs in a single atomic operation
        if inputs:
            # Create an array of INPUT structures
            input_array = (INPUT * len(inputs))(*inputs)
            
            # Send the inputs directly
            result = SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
            
            if result != len(inputs):
                error = ctypes.get_last_error()
                print(f"Error sending key sequence inputs: {error}")
                return False
        
        return True
    
    # If delay is needed, send inputs one by one with the specified delay
    for key, is_up in keys:
        if is_up:
            if not key_up(key):
                return False
        else:
            if not key_down(key):
                return False
        
        time.sleep(delay)
    
    return True

def send_multiple_inputs(inputs):
    """
    Send multiple input events in a single batch to the Windows API.
    This ensures that all inputs are processed atomically without interruption.
    
    Args:
        inputs (list): List of INPUT structures to send
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not inputs:
        return True
    
    # Create an array of INPUT structures
    input_array = (INPUT * len(inputs))(*inputs)
    
    # Send the inputs
    result = SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
    
    if result != len(inputs):
        error = ctypes.get_last_error()
        print(f"Error sending multiple inputs: {error}")
        return False
    
    return True

def create_key_input(key, is_up):
    """
    Create an INPUT structure for a key event.
    
    Args:
        key (str): The key to press or release
        is_up (bool): True for key up, False for key down
    
    Returns:
        INPUT: The input structure
    """
    if key not in VK_CODES:
        print(f"Error: Key '{key}' not found in VK_CODES")
        return None
    
    vk_code = VK_CODES[key]
    
    # Create input structure
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

def create_mouse_input(is_middle_down):
    """
    Create an INPUT structure for a middle mouse button event.
    
    Args:
        is_middle_down (bool): True for middle button down, False for middle button up
    
    Returns:
        INPUT: The input structure
    """
    # Create input structure
    return INPUT(
        type=INPUT_MOUSE,
        union=INPUT_UNION(
            mi=MOUSEINPUT(
                dx=0,
                dy=0,
                mouseData=0,
                dwFlags=MOUSEEVENTF_MIDDLEDOWN if is_middle_down else MOUSEEVENTF_MIDDLEUP,
                time=0,
                dwExtraInfo=ctypes.pointer(wintypes.ULONG(0))
            )
        )
    )

def middle_mouse_down():
    """
    Send a middle mouse button down event using the Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create middle mouse down input
    input_struct = create_mouse_input(True)
    
    # Send input directly
    result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
    
    if result != 1:
        error = ctypes.get_last_error()
        print(f"Error sending middle mouse down event: {error}")
        return False
    
    return True

def middle_mouse_up():
    """
    Send a middle mouse button up event using the Windows API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create middle mouse up input
    input_struct = create_mouse_input(False)
    
    # Send input directly
    result = SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
    
    if result != 1:
        error = ctypes.get_last_error()
        print(f"Error sending middle mouse up event: {error}")
        return False
    
    return True

def click_middle_mouse():
    """
    Click the middle mouse button (press and release).
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create both middle mouse down and up inputs
    inputs = []
    inputs.append(create_mouse_input(True))   # Middle mouse down
    inputs.append(create_mouse_input(False))  # Middle mouse up
    
    # Send all inputs in a single atomic operation
    if inputs:
        # Create an array of INPUT structures
        input_array = (INPUT * len(inputs))(*inputs)
        
        # Send the inputs directly
        result = SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
        
        if result != len(inputs):
            error = ctypes.get_last_error()
            print(f"Error sending middle mouse click inputs: {error}")
            return False
    
    return True

def send_sector_change(cancel_key, old_attack_key, new_attack_key, release_delay=0.0):
    """
    Send a precise sector change sequence as a single atomic operation for maximum speed.
    All key events are sent in a single Windows API call to minimize latency.
    
    If cancel_key is "middle_mouse", it will use the middle mouse button instead of a keyboard key.
    
    Args:
        cancel_key (str): The cancel key or "middle_mouse" for middle mouse button
        old_attack_key (str): The old attack key
        new_attack_key (str): The new attack key
        release_delay (float): Not used anymore, kept for compatibility
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create all inputs in a single array
    inputs = []
    
    # Check if we're using the middle mouse button for cancel
    if cancel_key == "middle_mouse":
        # 1. Press middle mouse button and release old attack key
        inputs.append(create_mouse_input(True))  # Middle mouse down
        inputs.append(create_key_input(old_attack_key, True))
        
        # 2. Release middle mouse button
        inputs.append(create_mouse_input(False))  # Middle mouse up
    else:
        # 1. Press cancel key and release old attack key
        inputs.append(create_key_input(cancel_key, False))
        inputs.append(create_key_input(old_attack_key, True))
        
        # 2. Release cancel key
        inputs.append(create_key_input(cancel_key, True))
    
    # 3. Press new attack key
    inputs.append(create_key_input(new_attack_key, False))
    
    # Remove any None values (in case a key wasn't found in VK_CODES)
    inputs = [inp for inp in inputs if inp is not None]
    
    # Send all inputs in a single atomic operation
    if inputs:
        # Create an array of INPUT structures
        input_array = (INPUT * len(inputs))(*inputs)
        
        # Send the inputs directly to avoid function call overhead
        result = SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
        
        if result != len(inputs):
            error = ctypes.get_last_error()
            print(f"Error sending sector change inputs: {error}")
            return False
    
    return True

# Test function
if __name__ == "__main__":
    print("Testing Windows API input module...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Type "Hello, World!"
    for char in "Hello, World!":
        press_key(char.lower())
        time.sleep(0.1)
    
    print("Test complete.")
