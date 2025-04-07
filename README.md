# Chakram X Alternative Control System for Mortal Online 2

This is a minimal prototype for an alternative control system for Mortal Online 2 using the Chakram X mouse joystick in analog mode.

## Requirements

- Python 3.6+
- pygame 2.1.2
- interception-python 1.1.0 (for enhanced input simulation)
- Chakram X mouse with joystick in analog mode
- Mortal Online 2

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. (Optional but recommended) Install the Interception driver for enhanced input simulation:
   - Download the Interception driver from [the official GitHub repository](https://github.com/oblitum/Interception)
   - Run the installer as administrator
   - Restart your computer after installation

## Usage

1. Make sure your Chakram X mouse is connected and the joystick is in analog mode
2. Run the application:

```bash
python run.py
```

3. The application will display a visualization of the joystick sectors and the current state
4. Move the joystick to control the attacks in Mortal Online 2

The application will automatically use the Interception driver if installed, providing more reliable and precise input simulation. If the Interception driver is not available, it will fall back to using the Windows API.

### Configuration Editor

You can customize the controller settings using the built-in configuration editor:

```bash
python run.py --config
```

The configuration editor allows you to:
- Adjust the deadzone size
- Customize sector boundaries
- Change key mappings
- Modify visualization settings

All settings are saved to `~/.chakram_controller/config.json` and will be loaded automatically when you start the application.

### Headless Mode

You can also run the application in headless mode (without GUI) which is useful for running in the background:

```bash
python run.py --headless
```

To exit headless mode, press Ctrl+C in the terminal.

### Command-line Options

The application supports the following command-line options:

- `--config`: Launch the configuration editor
- `--headless`: Run in headless mode (no GUI)
- `--joystick ID`: Specify the joystick ID to use (default: 0)
- `--check`: Run joystick check utility to verify your setup

Example:

```bash
python run.py --headless --joystick 1
```

## How It Works

The application divides the 360-degree joystick field into 4 sectors, each corresponding to one of the 4 attack directions in Mortal Online 2:

- **Overhead** (Left sector, 225° to 315°): Key "1"
- **Right** (Top sector, 315° to 45°): Key "2"
- **Thrust** (Right sector, 45° to 135°): Key "3"
- **Left** (Bottom sector, 135° to 225°): Key "4"

The cancel button is mapped to the middle mouse button by default.

When you move the joystick:
1. Moving from the neutral position (center) to a sector presses the corresponding attack key
2. Moving from one sector to another first presses the cancel button (middle mouse button), releases the current attack key, releases the cancel button, and then presses the new attack key
3. Returning to the neutral position releases all keys

## Configuration

You can customize the controller settings using the configuration editor:

```bash
python run.py --config
```

This provides a user-friendly interface to adjust:

- **Deadzone**: Radius of the center deadzone (0.0 to 0.5)
- **Release Delay**: Time between releasing attack and cancel buttons (in seconds)
- **Sector Change Cooldown**: Minimum time between sector changes to prevent double hits (in seconds)
- **Sector Boundaries**: Angle ranges for each attack direction
- **Key Mappings**: Keyboard keys for each action
- **Visualization Settings**: Window size and appearance

All settings are saved to `~/.chakram_controller/config.json` and loaded automatically when you start the application.

Alternatively, you can manually edit the configuration file located at:
```
~/.chakram_controller/config.json
```

## Input System

The application uses a sophisticated input system with two implementations:

1. **Interception Driver (Recommended)**: Uses the interception-python library to provide low-level keyboard and mouse input simulation at the driver level, bypassing the Windows input stack for maximum reliability and precision.

2. **Windows API Fallback**: Automatically used if the Interception driver is not available, providing good compatibility with most systems.

### Testing the Input System

You can test the input system using the included test scripts:

```bash
python test_interception_comprehensive.py
```

This will launch an interactive test menu that allows you to test all aspects of the input system, including keyboard input, mouse buttons, key sequences, and sector changes.

## Troubleshooting

If you encounter issues with joystick detection:
1. Make sure the Chakram X mouse is properly connected
2. Verify that the joystick is in analog mode
3. Run the joystick check utility: `python run.py --check`

If you have issues with key presses not being detected in Mortal Online 2:
1. Make sure Mortal Online 2 is in focus
2. Verify that the key mappings match your in-game settings
3. Try installing the Interception driver for more reliable input simulation
4. If using the Interception driver, make sure it's properly installed and running

### Interception Driver Issues

If you encounter issues with the Interception driver:

1. Make sure the driver is properly installed and running
2. Check if you have administrator privileges
3. Verify that no other application is exclusively capturing input
4. Look for error messages in the console output

## Recent Fixes

### Sector Change Cooldown to Prevent Double Hits

Fixed an issue where rapid sector transitions could cause double hits even when the user didn't press the button twice. The fix implements:

1. A configurable cooldown period (default: 150ms) between sector changes to prevent unintended double hits
2. The cooldown timer starts after a sector change is completed and prevents any new sector changes until the cooldown expires
3. This prevents the controller from registering multiple sector changes in quick succession when the user only intended to make a single movement

### Key Press Handling During Quick Sector Changes

Fixed an issue where rapid sector transitions could cause key presses to be processed in the wrong order. The fix ensures that:

1. The cancel key is fully registered before releasing the old attack key
2. A small delay (10ms) is added between pressing the cancel key and releasing the old attack key
3. The release delay between actions has been increased from 50ms to 80ms for better reliability

This addresses the bug where the game would sometimes process the key release before the cancel key press during very quick sector changes.
