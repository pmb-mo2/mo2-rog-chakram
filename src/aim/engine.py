"""Core Aim Mode engine handling state and mouse speed changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .config import AimConfig
from .smoothing import EMA
from .system import get_mouse_speed, set_mouse_speed


@dataclass
class MouseEvent:
    """Simple representation of a mouse event."""

    type: str  # 'move' | 'button'
    dx: int = 0
    dy: int = 0
    button: str | None = None
    pressed: bool | None = None


class AimEngine:
    """Engine implementing Aim Mode logic."""

    def __init__(self, cfg: AimConfig):
        self.cfg = cfg
        self.enabled = cfg.enabled
        self.aiming = False
        self._owns_lmb = False
        self._ema_x = EMA(cfg.smoothing.alpha)
        self._ema_y = EMA(cfg.smoothing.alpha)
        self._orig_speed: int | None = None

    # Button handling -------------------------------------------------
    def on_button(self, pressed: bool) -> List[Tuple[str, str]]:
        """Handle activation button events.

        Returns a list of synthetic LMB events (button, action).
        """
        if not self.enabled:
            print("AimEngine: activation button event ignored (disabled)")
            return []
        out: List[Tuple[str, str]] = []
        if self.cfg.mode == "hold":
            self.aiming = pressed
        else:  # toggle
            if pressed:
                self.aiming = not self.aiming

        print(f"AimEngine: button {'pressed' if pressed else 'released'}, aiming={self.aiming}")

        if self.aiming and self._orig_speed is None:
            self._orig_speed = get_mouse_speed()
            new_speed = max(1, int(self._orig_speed * self.cfg.scale))
            set_mouse_speed(new_speed)
            print(f"AimEngine: mouse speed set to {new_speed}")
        elif not self.aiming and self._orig_speed is not None:
            set_mouse_speed(self._orig_speed)
            print(f"AimEngine: mouse speed restored to {self._orig_speed}")
            self._orig_speed = None

        if self.cfg.auto_lmb:
            if self.aiming and not self._owns_lmb:
                out.append(("LMB", "down"))
                self._owns_lmb = True
                print("AimEngine: auto LMB down")
            elif not self.aiming and self._owns_lmb:
                out.append(("LMB", "up"))
                self._owns_lmb = False
                print("AimEngine: auto LMB up")
        return out

    # Movement passthrough --------------------------------------------
    def scale_move(self, dx: int, dy: int) -> Tuple[int, int]:
        """Return mouse movement, applying smoothing when active."""
        if not (self.enabled and self.aiming):
            return dx, dy

        if self.cfg.smoothing.type == "ema":
            dx = int(round(self._ema_x.update(dx)))
            dy = int(round(self._ema_y.update(dy)))
        return dx, dy
