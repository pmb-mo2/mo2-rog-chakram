"""Command-line helpers for managing Aim Mode configuration."""

from __future__ import annotations

import argparse
from typing import Dict

from ..aim.config import AimConfig
from ..io import config_store


def _load() -> Dict:
    cfg = config_store.load_config()
    aim_cfg = AimConfig.from_dict(cfg.get("aim", {}))
    cfg["aim"] = aim_cfg.to_dict()
    return cfg


def _save(cfg: Dict) -> None:
    config_store.save_config(cfg)


def cmd_status() -> None:
    cfg = _load()
    aim_cfg = AimConfig.from_dict(cfg["aim"])
    print("Aim Mode configuration:")
    for k, v in aim_cfg.to_dict().items():
        print(f"  {k}: {v}")


def cmd_toggle(enable: bool) -> None:
    cfg = _load()
    cfg["aim"]["enabled"] = enable
    _save(cfg)
    state = "enabled" if enable else "disabled"
    print(f"Aim Mode {state}.")


def cmd_set(pairs: list[str]) -> None:
    cfg = _load()
    aim = cfg["aim"]
    for item in pairs:
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        if key in {"scale", "scale_x", "scale_y"}:
            aim[key] = float(val)
        elif key in {"auto_lmb"}:
            aim[key] = bool(int(val)) if val in {"0", "1"} else val.lower() in {"true", "yes"}
        elif key in {"min_step", "fallback_speed"}:
            aim[key] = int(val)
        else:
            aim[key] = val
    _save(cfg)
    print("Aim configuration updated.")


def cmd_test() -> None:
    cfg = _load()
    aim_cfg = AimConfig.from_dict(cfg["aim"])
    from ..aim.engine import AimEngine

    engine = AimEngine(aim_cfg)
    engine.on_button(True)
    print("Enter dx dy pairs, Ctrl+D to end:")
    try:
        while True:
            line = input("dx dy> ")
            if not line:
                continue
            dx, dy = map(int, line.split())
            sx, sy = engine.scale_move(dx, dy)
            print(f"scaled: {sx} {sy}")
    except (EOFError, KeyboardInterrupt):
        pass


def add_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("Aim Mode")
    group.add_argument("--aim", choices=["enable", "disable"], help="Enable or disable Aim Mode")
    group.add_argument("--aim-status", action="store_true", help="Print Aim Mode configuration")
    group.add_argument("--aim-test", action="store_true", help="Interactive scaling test")
    group.add_argument("--aim-set", nargs="*", help="Set Aim Mode parameters (key=value)")


def handle_args(args: argparse.Namespace) -> bool:
    if args.aim:
        cmd_toggle(args.aim == "enable")
        return True
    if args.aim_status:
        cmd_status()
        return True
    if args.aim_test:
        cmd_test()
        return True
    if args.aim_set:
        cmd_set(args.aim_set)
        return True
    return False
