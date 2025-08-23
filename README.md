# Chakram X Alternative Control System for Mortal Online 2

This is an alternative control system for Mortal Online 2 using the Chakram X mouse joystick in analog mode. It features an adaptive control system with advanced movement prediction, combat mode, training exercises, and customizable settings.

## Table of Contents

- [Requirements](#requirements)
- [Showcase](#showcase)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Adaptive Control System](#adaptive-control-system)
- [Combat Mode](#combat-mode)
- [Alternative Mode](#alternative-mode)
- [Training Mode](#training-mode)
- [Configuration](#configuration)
- [Input System](#input-system)
- [Aim Mode](#aim-mode)
- [Troubleshooting](#troubleshooting)
- [Compatibility](#compatibility)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.6+
- pygame 2.1.2
- interception-python 1.1.0 (for enhanced input simulation)
- Chakram X mouse with joystick in analog mode
- Mortal Online 2

## Showcase 
### Swapping Blocks and Attacks Demo
[![Swapping Blocks and Attacks Demo](https://img.youtube.com/vi/NKblz9ZrwEw/hqdefault.jpg)](https://youtu.be/NKblz9ZrwEw)

### Random Targets Exercise Demo
[![Training Type 1 Demo](https://img.youtube.com/vi/GUGOk6ite6w/hqdefault.jpg)](https://youtu.be/GUGOk6ite6w)

### Circle Targets Exercise Demo
[![Training Type 2 Demo](https://img.youtube.com/vi/Ac4GGqok_xM/hqdefault.jpg)](https://youtu.be/Ac4GGqok_xM)

### Swapping Attacks Demo (slowly)
[![Swapping Attacks Demo (slowly)](https://img.youtube.com/vi/yTiKB-XuKkQ/hqdefault.jpg)](https://youtu.be/yTiKB-XuKkQ)

### Swapping Between 2 Attacks Demo
[![Swapping Between 2 Attacks](https://img.youtube.com/vi/Vz8Ny_bGD6U/hqdefault.jpg)](https://youtu.be/Vz8Ny_bGD6U)

## Quickstart | python version

1. Install the required dependencies and drivers (see [Installation](#installation))
2. Configure your Chakram X mouse to use analog joystick mode
3. Start the tool with `python run.py` or download binary version and start with `run.exe`
4. Launch Mortal Online 2
5. In MO2 settings:
   - Set attack style to "movement keys"
   - Set attack buttons to arrow keys
   - Enable "button charges attack" option
   - Set feint to MOUSE3
6. Return to the game and enjoy enhanced control!

For advanced configuration options, run `python run.py --config` to open the configuration editor.

## Installation

1. Clone this repository or download the files:
   ```bash
   git clone https://github.com/pmb-mo2/mo2-rog-chakram.git
   cd mo2-rog-chakram
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional but recommended) Install the Interception driver for enhanced input simulation:
   - Download the Interception driver from [the official GitHub repository](https://github.com/oblitum/Interception)
   - Run the installer as administrator
   - Restart your computer after installation
   - See [INTERCEPTION_USAGE.md](INTERCEPTION_USAGE.md) for detailed instructions

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
- Configure adaptive control settings
- Toggle combat mode features
- Adjust alternative mode settings
- Modify visualization settings

All settings are saved to `~/.chakram_controller/config.json` and will be loaded automatically when you start the application.

### Training Mode

The application includes a training mode to help you practice using the controller effectively:

- **Random Targets Exercise**: Practice hitting randomly appearing sectors
- **Circle Targets Exercise**: Practice precision control with moving targets

To activate training mode, press:
- `T` to start the sector training mode
- `Y` to start the precision circle training mode
- `1-5` to change difficulty levels (1=Easy, 5=Master)

Training mode helps you build muscle memory for quick and accurate attacks in the game.

### Headless Mode

You can also run the application in headless mode (without GUI) which is useful for running in the background:

```bash
python run.py --headless
```

To exit headless mode, press Ctrl+C in the terminal.

### Command-line Options

The application supports the following command-line options:

| Option | Description |
|--------|-------------|
| `--config` | Launch the configuration editor |
| `--headless` | Run in headless mode (no GUI) |
| `--joystick ID` | Specify the joystick ID to use (default: 0) |
| `--check` | Run joystick check utility to verify your setup |

Example:

```bash
python run.py --headless --joystick 1
```

## How It Works

The application divides the 360-degree joystick field into 4 sectors, each corresponding to one of the 4 attack directions in Mortal Online 2:

- **Overhead** (Left sector, 225° to 315°): Key "Up"
- **Right** (Top sector, 315° to 45°): Key "Right"
- **Thrust** (Right sector, 45° to 135°): Key "Down"
- **Left** (Bottom sector, 135° to 225°): Key "Left"

The cancel button is mapped to the middle mouse button by default.

When you move the joystick:
1. Moving from the neutral position (center) to a sector presses the corresponding attack key
2. Moving from one sector to another first presses the cancel button (middle mouse button), releases the current attack key, releases the cancel button, and then presses the new attack key
3. Returning to the neutral position releases all keys

## Adaptive Control System

The adaptive control system is a powerful feature that adjusts controller behavior based on your movement patterns:

### Dynamic Deadzone
- Automatically adjusts deadzone size based on your movement speed and game state
- Smaller deadzone for quick, precise movements
- Larger deadzone for slower, more deliberate movements
- Prevents accidental sector changes during combat

### Movement Prediction
- Predicts your intended sector changes before you complete the motion
- Provides faster, more responsive control
- Increases accuracy during fast-paced combat
- Adapts to your personal movement style over time

### Smart Transitions
- Adjusts transition timing based on your movement speed
- Optimizes for smooth, reliable sector changes
- Prevents accidental double-hits or missed inputs
- Provides consistent control regardless of movement speed

To enable or disable adaptive control features, use the configuration editor:
```bash
python run.py --config
```

## Combat Mode

Combat mode provides optimized controller settings for combat situations:

- **Reduced Deadzone**: Smaller deadzone for faster, more responsive attacks
- **Faster Transitions**: Quicker transitions between attack directions
- **Optimized Prediction**: Enhanced movement prediction during combat
- **Automatic Detection**: Can automatically detect when you're in combat (optional)

To toggle combat mode:
- Press the combat mode key (default: `C`)
- Press the second joystick button (if available)

Combat mode status is displayed in the visualization window.

## Alternative Mode

The application also features an alternative mode that can be activated by holding down a configurable key (default: left Alt). This mode is designed for different gameplay scenarios and works as follows:

When alternative mode is active:
1. Moving the joystick from the neutral position to a sector:
   - Moves the cursor 20px (configurable) in the corresponding direction
   - Presses and holds the right mouse button
2. Moving from one sector to another:
   - Releases the right mouse button
   - Moves the cursor 20px (configurable) in the new direction
   - Presses and holds the right mouse button again
3. Returning to the neutral position (center) releases the right mouse button

The sector mapping in alternative mode:
- **Top sector** (Right): Moves cursor up
- **Bottom sector** (Left): Moves cursor down
- **Left sector** (Overhead): Moves cursor left
- **Right sector** (Thrust): Moves cursor right

To toggle between standard and alternative modes, simply hold or release the alternative mode key (default: left Alt).

## Training Mode

The training mode helps you practice and improve your skills with the controller:

### Random Targets Exercise
- Targets appear in random sectors
- You must move the joystick to the highlighted sector
- Trains rapid, accurate sector changes
- Measures response time and accuracy

### Circle Targets Exercise
- Circular targets appear at various positions
- You must move and hold the cursor within the circle
- Trains precise cursor control using the alternative mode
- Measures time-on-target and precision

Both exercises feature 5 difficulty levels (Easy to Master) that adjust target size, appearance rate, and movement speed.

Training statistics are displayed at the end of each session, helping you track your progress over time.

## Configuration

You can customize the controller settings using the configuration editor:

```bash
python run.py --config
```

This provides a user-friendly interface to adjust:

- **Deadzone**: Radius of the center deadzone (0.0 to 0.5)
- **Release Delay**: Time between releasing attack and cancel buttons (in seconds)
- **Sector Change Cooldown**: Minimum time between sector changes to prevent double hits (in seconds)
- **Adaptive Control Settings**:
  - **Dynamic Deadzone**: Enable/disable and adjust min/max factors
  - **Movement Prediction**: Enable/disable and adjust prediction time and confidence threshold
  - **Transition Smoothness**: Adjust base smoothness and min/max factors
- **Combat Mode Settings**:
  - **Combat Mode Key**: Key to toggle combat mode (default: C)
  - **Combat Deadzone**: Smaller deadzone size for combat mode
  - **Combat Transition Smoothness**: Faster transitions for combat mode
  - **Combat Detection**: Enable/disable automatic combat detection
- **Alternative Mode Settings**:
  - **Alt Mode Key**: Key to hold for activating alternative mode (default: left Alt)
  - **Cursor Offset**: Distance in pixels to move the cursor in alternative mode (default: 20px)
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

## Aim Mode

Aim Mode provides a temporary precision mode by lowering system mouse
sensitivity and optionally auto-holding the left mouse button. It is enabled by
default and listens to the mouse back button (`mouse4`). Configuration lives in
`~/.chakram_controller/config.json` under the `aim` section and can be
adjusted via command line:

```bash
python run.py --aim-status        # show current settings
python run.py --aim enable        # enable Aim Mode
python run.py --aim-set scale=0.5 # update parameters
```

For more details see [docs/AIM_MODE.md](docs/AIM_MODE.md).

## Troubleshooting

### Joystick Detection Issues

If you encounter issues with joystick detection:
1. Make sure the Chakram X mouse is properly connected
2. Verify that the joystick is in analog mode
3. Run the joystick check utility: `python run.py --check`
4. Try using a different USB port
5. Check if the joystick is recognized by Windows in Control Panel > Devices and Printers

### Input Simulation Issues

If you have issues with key presses not being detected in Mortal Online 2:
1. Make sure Mortal Online 2 is in focus
2. Verify that the key mappings match your in-game settings
3. Try installing the Interception driver for more reliable input simulation
4. If using the Interception driver, make sure it's properly installed and running
5. Run the application as administrator: right-click `run.py` and select "Run as administrator"

### Adaptive Control Issues

If the adaptive control system isn't working as expected:
1. Make sure adaptive control is enabled in the configuration
2. Try adjusting the sensitivity parameters in the configuration editor
3. Reset to default settings if you've made extensive changes
4. Try disabling individual features (dynamic deadzone, prediction) to isolate issues

### Combat Mode Issues

If combat mode isn't working properly:
1. Verify the combat mode key is correctly set in the configuration
2. Check if automatic game state detection is interfering with manual toggling
3. Try adjusting the combat timeout value if it's switching out of combat too quickly

### Interception Driver Issues

If you encounter issues with the Interception driver:

1. Make sure the driver is properly installed and running
2. Check if you have administrator privileges
3. Verify that no other application is exclusively capturing input
4. Look for error messages in the console output
5. Try reinstalling the driver following the instructions in [INTERCEPTION_USAGE.md](INTERCEPTION_USAGE.md)

## Compatibility

This application has been tested with:

- Windows 10 and 11
- Python 3.6, 3.7, 3.8, 3.9, and 3.10
- ROG Chakram X mouse (firmware version 1.00.00 and above)
- Mortal Online 2 (latest version)

Other joystick-enabled mice may work but have not been extensively tested.

## Contributing

Contributions are welcome! If you'd like to contribute to this project:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Submit a pull request

Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
