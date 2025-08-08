import sys
import ctypes
import ctypes.util
import pygame
from src.config import ALT_MODE_CURSOR_OFFSET

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
    def __init__(self, modifiers, scale=ALT_MODE_CURSOR_OFFSET, pointer_lock=True, lock_center=True, invert_y=False):
        self.modifiers = modifiers
        self.scale = scale if scale else 1
        self.pointer_lock = pointer_lock
        self.lock_center = lock_center
        self.invert_y = invert_y
        self.anchor = None

    def initialize(self):
        pygame.event.pump()
        self.anchor = _get_cursor_pos()
        print(f"Mouse axes active. Modifiers: {self.modifiers}")

    def _modifier_pressed(self):
        keys = pygame.key.get_pressed()
        buttons = pygame.mouse.get_pressed(5)
        for mod in self.modifiers:
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

    def get_axes(self):
        pygame.event.pump()
        cur = _get_cursor_pos()
        if self.anchor is None:
            self.anchor = cur
            return 0.0, 0.0
        if self._modifier_pressed():
            self.anchor = cur
            return 0.0, 0.0
        dx = cur[0] - self.anchor[0]
        dy = cur[1] - self.anchor[1]
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
        return x, y
