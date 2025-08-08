import sys
import ctypes
import ctypes.util
import time
import math
import pygame
from src.config import (
    ALT_MODE_CURSOR_OFFSET,
    SECTORS,
    KEY_MAPPINGS,
    DEADZONE,
)
from src.win_input import key_down, key_up, right_mouse_down, right_mouse_up

MOUSE_BUTTONS = {
    "left_mouse": 0,
    "middle_mouse": 1,
    "right_mouse": 2,
    "mouse4": 3,
    "mouse5": 4,
}

KEY_OVERRIDES = {
    "alt": [pygame.K_LALT, pygame.K_RALT],
    "ctrl": [pygame.K_LCTRL, pygame.K_RCTRL],
    "shift": [pygame.K_LSHIFT, pygame.K_RSHIFT],
}

# Determine platform
_platform = "win" if sys.platform.startswith("win") else "x11"

if _platform == "win":
    user32 = ctypes.windll.user32

    class _POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    def _get_cursor_pos():
        pt = _POINT()
        if not user32.GetCursorPos(ctypes.byref(pt)):
            return pygame.mouse.get_pos()
        return pt.x, pt.y

    def _set_cursor_pos(x, y):
        user32.SetCursorPos(int(x), int(y))

else:
    _x11 = None
    _lib_name = ctypes.util.find_library("X11")
    if _lib_name:
        try:
            _x11 = ctypes.cdll.LoadLibrary(_lib_name)
        except OSError:
            _x11 = None
    if _x11 is None:
        print("Warning: X11 not available; pointer lock disabled")

    def _get_cursor_pos():
        if _x11 is None:
            return pygame.mouse.get_pos()
        dpy = _x11.XOpenDisplay(None)
        if not dpy:
            return pygame.mouse.get_pos()
        root = _x11.XDefaultRootWindow(dpy)
        root_x = ctypes.c_int()
        root_y = ctypes.c_int()
        win_x = ctypes.c_int()
        win_y = ctypes.c_int()
        mask = ctypes.c_uint()
        child = ctypes.c_ulong()
        root_ret = ctypes.c_ulong()
        _x11.XQueryPointer(dpy, root, ctypes.byref(root_ret), ctypes.byref(child),
                           ctypes.byref(root_x), ctypes.byref(root_y),
                           ctypes.byref(win_x), ctypes.byref(win_y),
                           ctypes.byref(mask))
        _x11.XCloseDisplay(dpy)
        return root_x.value, root_y.value

    def _set_cursor_pos(x, y):
        if _x11 is None:
            return
        dpy = _x11.XOpenDisplay(None)
        if not dpy:
            return
        root = _x11.XDefaultRootWindow(dpy)
        _x11.XWarpPointer(dpy, 0, root, 0, 0, 0, 0, int(x), int(y))
        _x11.XFlush(dpy)
        _x11.XCloseDisplay(dpy)


class MouseAxes:
    STATE_IDLE = 0
    STATE_AIMING = 1
    STATE_COOLDOWN = 2

    def __init__(
        self,
        modifiers,
        scale=ALT_MODE_CURSOR_OFFSET,
        pointer_lock=True,
        lock_center=True,
        invert_y=False,
        attack_on_modifier_release=False,
        aim_modifier=None,
        aim_requires_movement=True,
        aim_direction_memory_ms=250,
        attack_press_duration_ms=50,
        post_attack_cooldown_ms=200,
        block_while_held=False,
        block_key=None,
    ):
        self.modifiers = modifiers
        self.scale = scale if scale else 1
        self.pointer_lock = pointer_lock
        self.lock_center = lock_center
        self.invert_y = invert_y

        # Attack on release settings
        self.attack_on_modifier_release = attack_on_modifier_release
        self.aim_modifier = aim_modifier
        self.aim_requires_movement = aim_requires_movement
        self.aim_direction_memory_ms = aim_direction_memory_ms
        self.attack_press_duration_ms = attack_press_duration_ms
        self.post_attack_cooldown_ms = post_attack_cooldown_ms
        self.block_while_held = block_while_held
        self.block_key = block_key

        # Runtime state
        self.anchor = None
        self.state = self.STATE_IDLE
        self.last_sector = None
        self.last_sector_ts = 0.0
        self.cooldown_until_ts = 0.0
        self.prev_mod_pressed = False
        self.block_pressed = False

    def initialize(self):
        pygame.event.pump()
        self.anchor = _get_cursor_pos()
        print(f"Mouse axes active. Modifiers: {self.modifiers}")

    def _is_modifier_pressed(self, mod):
        keys = pygame.key.get_pressed()
        buttons = pygame.mouse.get_pressed(5)
        if mod in MOUSE_BUTTONS and buttons[MOUSE_BUTTONS[mod]]:
            return True
        codes = KEY_OVERRIDES.get(mod)
        if codes and any(keys[c] for c in codes):
            return True
        try:
            code = pygame.key.key_code(mod)
            if keys[code]:
                return True
        except Exception:
            pass
        return False

    def _determine_sector(self, x, y):
        distance = math.sqrt(x * x + y * y)
        if distance < DEADZONE:
            return None
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
        for name, rng in SECTORS.items():
            start = rng["start"]
            end = rng["end"]
            if start > end:
                if angle >= start or angle <= end:
                    return name
            else:
                if start <= angle <= end:
                    return name
        return None

    def _press_block(self):
        if not self.block_key:
            return
        if self.block_key == "right_mouse":
            right_mouse_down()
        else:
            key_down(self.block_key)
        self.block_pressed = True

    def _release_block(self):
        if not self.block_key or not self.block_pressed:
            return
        if self.block_key == "right_mouse":
            right_mouse_up()
        else:
            key_up(self.block_key)
        self.block_pressed = False

    def get_axes(self):
        pygame.event.pump()
        cur = _get_cursor_pos()
        if self.anchor is None:
            self.anchor = cur
            return 0.0, 0.0

        now_ms = time.perf_counter() * 1000
        if self.state == self.STATE_COOLDOWN and now_ms >= self.cooldown_until_ts:
            self.state = self.STATE_IDLE

        mod_pressed = self._is_modifier_pressed(self.aim_modifier) if self.aim_modifier else False
        just_released = self.prev_mod_pressed and not mod_pressed

        dx = cur[0] - self.anchor[0]
        dy = cur[1] - self.anchor[1]

        other_mod_pressed = any(
            self._is_modifier_pressed(m)
            for m in self.modifiers
            if m != self.aim_modifier
        )
        if other_mod_pressed:
            if self.pointer_lock:
                if not self.lock_center:
                    self.anchor = (self.anchor[0] + dx, self.anchor[1] + dy)
                _set_cursor_pos(*self.anchor)
            else:
                self.anchor = cur
            self.prev_mod_pressed = mod_pressed
            self.last_sector = None
            self.state = self.STATE_IDLE
            return 0.0, 0.0

        # Handle modifier held
        if mod_pressed and self.state != self.STATE_COOLDOWN:
            if self.state == self.STATE_IDLE:
                self.state = self.STATE_AIMING

            if self.invert_y:
                dy = -dy
            x = max(-1.0, min(1.0, dx / self.scale))
            y = max(-1.0, min(1.0, dy / self.scale))
            sector = self._determine_sector(x, y)
            if sector:
                self.last_sector = sector
                self.last_sector_ts = now_ms

            if self.block_while_held and not self.block_pressed:
                self._press_block()

            if self.pointer_lock:
                if not self.lock_center:
                    self.anchor = (self.anchor[0] + dx, self.anchor[1] + dy)
                _set_cursor_pos(*self.anchor)
            else:
                self.anchor = cur

            self.prev_mod_pressed = mod_pressed
            return 0.0, 0.0

        # Modifier just released
        if just_released:
            if self.block_while_held:
                self._release_block()

            if (
                self.attack_on_modifier_release
                and self.state == self.STATE_AIMING
            ):
                valid = True
                if self.aim_requires_movement:
                    if (
                        not self.last_sector
                        or now_ms - self.last_sector_ts > self.aim_direction_memory_ms
                    ):
                        valid = False
                if valid and self.last_sector:
                    attack_key = KEY_MAPPINGS.get(self.last_sector)
                    if attack_key:
                        key_down(attack_key)
                        time.sleep(self.attack_press_duration_ms / 1000.0)
                        key_up(attack_key)
                        self.cooldown_until_ts = now_ms + self.post_attack_cooldown_ms
                        self.state = self.STATE_COOLDOWN

            self.last_sector = None
            self.last_sector_ts = 0.0
            if self.state != self.STATE_COOLDOWN:
                self.state = self.STATE_IDLE

        # Standard axis processing
        if self.pointer_lock:
            if not self.lock_center:
                self.anchor = (self.anchor[0] + dx, self.anchor[1] + dy)
            _set_cursor_pos(*self.anchor)
        else:
            self.anchor = cur

        if self.invert_y:
            dy = -dy
        x = max(-1.0, min(1.0, dx / self.scale))
        y = max(-1.0, min(1.0, dy / self.scale))

        self.prev_mod_pressed = mod_pressed
        return x, y
