"""Core Aim Mode engine handling state and scaling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .config import AimConfig
from .smoothing import EMA


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
        self._rem_x = 0.0
        self._rem_y = 0.0

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

    # Movement scaling ------------------------------------------------
    def scale_move(self, dx: int, dy: int) -> Tuple[int, int]:
        """Scale mouse movement according to configuration."""
        if not (self.enabled and self.aiming):
            return dx, dy

        # Apply smoothing if enabled
        if self.cfg.smoothing.type == "ema":
            dx = int(round(self._ema_x.update(dx)))
            dy = int(round(self._ema_y.update(dy)))

        sx = self.cfg.scale_x if self.cfg.scale_x is not None else self.cfg.scale
        sy = self.cfg.scale_y if self.cfg.scale_y is not None else self.cfg.scale

        # Accumulate fractional remainders to effectively lower sensitivity
        self._rem_x += dx * sx
        self._rem_y += dy * sy
        fx = int(self._rem_x)
        fy = int(self._rem_y)
        self._rem_x -= fx
        self._rem_y -= fy

        # Ensure minimal step when a scaled movement is emitted
        if fx != 0 and abs(fx) < self.cfg.min_step:
            fx = self.cfg.min_step if fx > 0 else -self.cfg.min_step
        if fy != 0 and abs(fy) < self.cfg.min_step:
            fy = self.cfg.min_step if fy > 0 else -self.cfg.min_step
        return fx, fy
