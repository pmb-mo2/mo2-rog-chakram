import pytest

from src.aim.config import AimConfig
from src.aim.engine import AimEngine


def make_engine(**kwargs) -> AimEngine:
    if "smoothing" not in kwargs:
        kwargs["smoothing"] = {"type": "off"}
    cfg = AimConfig.from_dict(kwargs)
    return AimEngine(cfg)


def test_scale_move_basic():
    engine = make_engine(scale=0.5)
    engine.on_button(True)
    assert engine.scale_move(10, -10) == (5, -5)
    # small movements should accumulate when scaling is active
    assert engine.scale_move(1, 0) == (0, 0)
    assert engine.scale_move(1, 0) == (1, 0)


def test_hold_auto_lmb():
    engine = make_engine(mode="hold", auto_lmb=True)
    events = engine.on_button(True)
    assert ("LMB", "down") in events
    events = engine.on_button(False)
    assert ("LMB", "up") in events


def test_toggle_mode():
    engine = make_engine(mode="toggle", auto_lmb=False)
    assert engine.aiming is False
    engine.on_button(True)
    assert engine.aiming is True
    engine.on_button(True)
    assert engine.aiming is False


def test_config_defaults():
    cfg = AimConfig.from_dict({})
    assert cfg.scale == 0.1
    assert cfg.mode == "hold"
    assert cfg.enabled is True
    assert cfg.button == "mouse4"


def test_button_aliases():
    cfg = AimConfig.from_dict({"button": "mouse_back"})
    assert cfg.button == "mouse4"
    cfg = AimConfig.from_dict({"button": "back"})
    assert cfg.button == "mouse4"
