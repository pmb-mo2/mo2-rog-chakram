# Using Interception-Python for Keyboard and Mouse Input

This document explains how to use the interception-python library for simulating keyboard and mouse input in the Chakram Controller project.

## Overview

The Chakram Controller project uses the interception-python library to provide low-level keyboard and mouse input simulation. This library interfaces with the Interception driver, which allows for direct input simulation at the driver level, bypassing the Windows input stack.

## Requirements

1. **Interception Driver**: The Interception driver must be installed on your system. You can download it from [the official GitHub repository](https://github.com/oblitum/Interception).

2. **interception-python Package**: This Python package is already listed in the requirements.txt file and should be installed when you set up the project.

## Implementation

The project includes two implementations for input simulation:

1. **win_input.py**: The original implementation using a different API style.
2. **win_input_interception.py**: The newer implementation with more features and better fallback to Windows API.

Both modules provide similar functionality, but `win_input_interception.py` is recommended for new development.

## Key Features

The interception-python implementation provides the following key features:

1. **Keyboard Input**:
   - Key press, release, and click operations
   - Support for special keys (arrows, function keys, etc.)
   - Key sequences with precise timing

2. **Mouse Input**:
   - Mouse button press, release, and click operations
   - Support for left, right, and middle mouse buttons

3. **Sector Change**:
   - Special function for game sector changes
   - Support for using keyboard keys or middle mouse button as cancel

4. **Fallback Mechanism**:
   - Automatic fallback to Windows API if Interception driver is not available
   - Seamless experience regardless of driver availability

## Usage Examples

### Basic Keyboard Input

```python
from src.win_input_interception import initialize, cleanup, press_key

# Initialize the input module
initialize()

# Press a key
press_key('a')

# Clean up when done
cleanup()
```

### Key Combinations

```python
from src.win_input_interception import initialize, cleanup, key_down, key_up

# Initialize the input module
initialize()

# Press Ctrl+C
key_down('ctrl')
key_down('c')
key_up('c')
key_up('ctrl')

# Clean up when done
cleanup()
```

### Mouse Buttons

```python
from src.win_input_interception import initialize, cleanup, click_left_mouse, click_right_mouse

# Initialize the input module
initialize()

# Click the left mouse button
click_left_mouse()

# Click the right mouse button
click_right_mouse()

# Clean up when done
cleanup()
```

### Sector Change (Game-specific)

```python
from src.win_input_interception import initialize, cleanup, send_sector_change

# Initialize the input module
initialize()

# Change from left to right using Escape as cancel key
send_sector_change('esc', 'left', 'right')

# Change from up to down using middle mouse button as cancel
send_sector_change('middle_mouse', 'up', 'down')

# Clean up when done
cleanup()
```

## Test Scripts

The project includes several test scripts to demonstrate the functionality:

1. **test_interception.py**: Basic test of the Interception driver directly.
2. **test_interception_input.py**: Test of the win_input_interception.py module.
3. **test_interception_usage.py**: Another test of the win_input_interception.py module.
4. **test_interception_comprehensive.py**: Comprehensive test of all features with a menu-driven interface.

To run a test script, use:

```
python test_interception_comprehensive.py
```

## Troubleshooting

If you encounter issues with the Interception driver:

1. Make sure the driver is properly installed and running.
2. Check if you have administrator privileges.
3. Verify that no other application is exclusively capturing input.
4. Look for error messages in the console output.

If the Interception driver is not available, the module will automatically fall back to using the Windows API for input simulation, which should work in most cases but may not provide the same level of precision or reliability.

## References

- [Interception Driver](https://github.com/oblitum/Interception)
- [interception-python Package](https://pypi.org/project/interception-python/)
