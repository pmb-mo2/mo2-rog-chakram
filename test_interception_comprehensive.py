"""
Comprehensive test script for the interception-python library.
This script demonstrates all the capabilities of the win_input_interception.py module,
including keyboard input, mouse buttons, and mouse movement.
"""

import time
import sys
import os
from src.win_input_interception import (
    initialize, cleanup, 
    key_down, key_up, press_key, send_key_sequence,
    left_mouse_down, left_mouse_up, click_left_mouse,
    middle_mouse_down, middle_mouse_up, click_middle_mouse,
    right_mouse_down, right_mouse_up, click_right_mouse,
    send_sector_change
)

def print_menu():
    """Print the main menu."""
    print("\nInterception Comprehensive Test Menu")
    print("===================================")
    print("1. Test keyboard input")
    print("2. Test mouse buttons")
    print("3. Test key sequences")
    print("4. Test sector change")
    print("5. Test typing text")
    print("6. Run all tests")
    print("0. Exit")
    print("===================================")

def test_keyboard_input():
    """Test basic keyboard input functions."""
    print("\nTesting keyboard input...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Test individual key presses
    print("Testing individual key presses...")
    for key in ['a', 'b', 'c', 'd', 'e']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.5)
    
    # Test key down and up separately
    print("Testing key down and up separately...")
    print("Pressing shift key down...")
    key_down('shift')
    time.sleep(0.5)
    
    for key in ['h', 'e', 'l', 'l', 'o']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.2)
    
    print("Releasing shift key...")
    key_up('shift')
    time.sleep(0.5)
    
    # Test arrow keys
    print("Testing arrow keys...")
    for key in ['left', 'up', 'right', 'down']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.5)
    
    # Test function keys
    print("Testing function keys...")
    for key in ['f1', 'f2', 'f3', 'f4']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.5)
    
    # Test special keys
    print("Testing special keys...")
    for key in ['esc', 'tab', 'enter', 'backspace']:
        print(f"Pressing key: {key}")
        press_key(key)
        time.sleep(0.5)
    
    print("Keyboard input test complete.")

def test_mouse_buttons():
    """Test basic mouse input functions."""
    print("\nTesting mouse buttons...")
    
    # Wait for user to switch to a window where mouse clicks are visible
    print("Switch to a window where mouse clicks are visible in 3 seconds...")
    time.sleep(3)
    
    # Test left mouse button
    print("Testing left mouse button...")
    print("Left mouse down")
    left_mouse_down()
    time.sleep(0.5)
    
    print("Left mouse up")
    left_mouse_up()
    time.sleep(0.5)
    
    print("Left mouse click")
    click_left_mouse()
    time.sleep(0.5)
    
    # Test right mouse button
    print("Testing right mouse button...")
    print("Right mouse down")
    right_mouse_down()
    time.sleep(0.5)
    
    print("Right mouse up")
    right_mouse_up()
    time.sleep(0.5)
    
    print("Right mouse click")
    click_right_mouse()
    time.sleep(0.5)
    
    # Test middle mouse button
    print("Testing middle mouse button...")
    print("Middle mouse down")
    middle_mouse_down()
    time.sleep(0.5)
    
    print("Middle mouse up")
    middle_mouse_up()
    time.sleep(0.5)
    
    print("Middle mouse click")
    click_middle_mouse()
    time.sleep(0.5)
    
    print("Mouse buttons test complete.")

def test_key_sequences():
    """Test sending key sequences."""
    print("\nTesting key sequences...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Test key sequence with delay
    print("Testing key sequence with delay...")
    keys = [
        ('a', False),  # a down
        ('a', True),   # a up
        ('b', False),  # b down
        ('b', True),   # b up
        ('c', False),  # c down
        ('c', True)    # c up
    ]
    send_key_sequence(keys, delay=0.1)
    time.sleep(1)
    
    # Test key sequence without delay (atomic)
    print("Testing key sequence without delay (atomic)...")
    keys = [
        ('d', False),  # d down
        ('d', True),   # d up
        ('e', False),  # e down
        ('e', True),   # e up
        ('f', False),  # f down
        ('f', True)    # f up
    ]
    send_key_sequence(keys, delay=0)
    time.sleep(1)
    
    # Test key combination (Ctrl+A)
    print("Testing key combination (Ctrl+A)...")
    keys = [
        ('ctrl', False),  # Ctrl down
        ('a', False),     # A down
        ('a', True),      # A up
        ('ctrl', True)    # Ctrl up
    ]
    send_key_sequence(keys, delay=0.05)
    time.sleep(1)
    
    print("Key sequences test complete.")

def test_sector_change():
    """Test the sector change function."""
    print("\nTesting sector change...")
    
    # Wait for user to switch to a game or application
    print("Switch to a game or application in 3 seconds...")
    time.sleep(3)
    
    # Test with keyboard cancel key
    print("Testing sector change with keyboard cancel key...")
    print("Changing from 'left' to 'right' using 'esc' as cancel key")
    send_sector_change('esc', 'left', 'right')
    time.sleep(1)
    
    # Test with middle mouse button as cancel
    print("Testing sector change with middle mouse button...")
    print("Changing from 'up' to 'down' using middle mouse button")
    send_sector_change('middle_mouse', 'up', 'down')
    time.sleep(1)
    
    print("Sector change test complete.")

def test_typing_text():
    """Test typing a full text string."""
    print("\nTesting typing text...")
    
    # Wait for user to switch to a text editor
    print("Switch to a text editor in 3 seconds...")
    time.sleep(3)
    
    # Type a sentence
    text = "Hello, this is a test of the interception-python library!"
    print(f"Typing: '{text}'")
    
    for char in text:
        if char.isupper():
            # For uppercase letters, press shift + lowercase letter
            key_down('shift')
            press_key(char.lower())
            key_up('shift')
        elif char == ' ':
            press_key('space')
        elif char == ',':
            # For comma, just press the key directly
            press_key(',')
        elif char == '!':
            # For exclamation mark, press shift + 1
            key_down('shift')
            press_key('1')
            key_up('shift')
        elif char == '.':
            # For period, just press the key directly
            press_key('.')
        else:
            # For other characters, just press the key
            press_key(char.lower())
        
        time.sleep(0.05)  # Small delay between keypresses
    
    print("Typing text test complete.")

def run_all_tests():
    """Run all tests in sequence."""
    print("\nRunning all tests in sequence...")
    
    test_keyboard_input()
    time.sleep(1)
    
    test_mouse_buttons()
    time.sleep(1)
    
    test_key_sequences()
    time.sleep(1)
    
    test_sector_change()
    time.sleep(1)
    
    test_typing_text()
    
    print("\nAll tests completed.")

def main():
    """Main function to run the comprehensive test."""
    print("Starting interception-python comprehensive test...")
    
    # Initialize the input module
    if not initialize():
        print("Failed to initialize input module. Exiting.")
        return
    
    try:
        while True:
            print_menu()
            choice = input("Enter your choice (0-6): ")
            
            if choice == '1':
                test_keyboard_input()
            elif choice == '2':
                test_mouse_buttons()
            elif choice == '3':
                test_key_sequences()
            elif choice == '4':
                test_sector_change()
            elif choice == '5':
                test_typing_text()
            elif choice == '6':
                run_all_tests()
            elif choice == '0':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        # Clean up
        cleanup()
    
    print("Test program completed.")

if __name__ == "__main__":
    main()
