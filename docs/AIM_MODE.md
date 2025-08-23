# Aim Mode

Aim Mode slows down mouse movement and optionally auto-holds the left mouse button.
It is intended for precise aiming while a chosen activation button is held or toggled.

## Configuration

The global configuration file lives at `~/.chakram_controller/config.json` and
contains an `aim` section:

```
{
  "aim": {
    "enabled": true,
    "mode": "hold",
    "button": "mouse4",
    "auto_lmb": true,
    "scale": 0.2
  }
}
```

Only a subset of options is shown above. Missing keys are filled with defaults.

By default, Aim Mode listens to the `mouse4` button (commonly the back side
button on modern mice).

## CLI

Use `run.py` to adjust Aim Mode:

```bash
python run.py --aim-status        # print current configuration
python run.py --aim enable        # enable Aim Mode
python run.py --aim disable       # disable Aim Mode
python run.py --aim-set scale=0.5 # set new parameters
python run.py --aim-test          # interactive scaling test
```

## Warning

Aim Mode relies on low level input modification. Some games employ anti-cheat
systems that may flag such behaviour. Use at your own risk.
