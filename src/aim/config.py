from __future__ import annotations

"""Configuration handling for Aim Mode."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SmoothingConfig:
    """Configuration for smoothing filter."""

    type: str = "ema"
    alpha: float = 0.25


@dataclass
class TransitionConfig:
    """Configuration for ramp up/down transitions."""

    enable: bool = False
    ramp_up_ms: int = 40
    ramp_down_ms: int = 30


@dataclass
class AimConfig:
    """Top level configuration for Aim Mode."""

    enabled: bool = True
    mode: str = "hold"  # hold | toggle
    button: str = "mouse4"
    auto_lmb: bool = True
    scale: float = 0.2
    scale_x: Optional[float] = None
    scale_y: Optional[float] = None
    min_step: int = 1
    smoothing: SmoothingConfig = field(default_factory=SmoothingConfig)
    transition: TransitionConfig = field(default_factory=TransitionConfig)
    priority: str = "high"
    fallback_windows_speed: bool = False
    fallback_speed: int = 1

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AimConfig":
        """Create configuration from dictionary applying defaults."""
        smoothing = data.get("smoothing", {})
        transition = data.get("transition", {})
        return AimConfig(
            enabled=data.get("enabled", True),
            mode=data.get("mode", "hold"),
            button=data.get("button", "mouse4"),
            auto_lmb=data.get("auto_lmb", True),
            scale=data.get("scale", 0.2),
            scale_x=data.get("scale_x"),
            scale_y=data.get("scale_y"),
            min_step=data.get("min_step", 1),
            smoothing=SmoothingConfig(
                type=smoothing.get("type", "ema"),
                alpha=smoothing.get("alpha", 0.25),
            ),
            transition=TransitionConfig(
                enable=transition.get("enable", False),
                ramp_up_ms=transition.get("ramp_up_ms", 40),
                ramp_down_ms=transition.get("ramp_down_ms", 30),
            ),
            priority=data.get("priority", "high"),
            fallback_windows_speed=data.get("fallback_windows_speed", False),
            fallback_speed=data.get("fallback_speed", 1),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to plain dictionary."""
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "button": self.button,
            "auto_lmb": self.auto_lmb,
            "scale": self.scale,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "min_step": self.min_step,
            "smoothing": {
                "type": self.smoothing.type,
                "alpha": self.smoothing.alpha,
            },
            "transition": {
                "enable": self.transition.enable,
                "ramp_up_ms": self.transition.ramp_up_ms,
                "ramp_down_ms": self.transition.ramp_down_ms,
            },
            "priority": self.priority,
            "fallback_windows_speed": self.fallback_windows_speed,
            "fallback_speed": self.fallback_speed,
        }
