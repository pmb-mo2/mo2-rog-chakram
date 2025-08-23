"""Utility functions for reading and writing the global config."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".chakram_controller")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_config() -> Dict[str, Any]:
    """Load configuration dictionary from disk."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_config(cfg: Dict[str, Any]) -> None:
    """Persist configuration dictionary to disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
