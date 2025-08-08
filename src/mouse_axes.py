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

class MouseAxes:
    def __init__(self, modifiers, scale=ALT_MODE_CURSOR_OFFSET):
        self.modifiers = modifiers
        self.scale = scale if scale else 1
        self.last_pos = None

    def initialize(self):
        pygame.event.pump()
        self.last_pos = pygame.mouse.get_pos()
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
        pos = pygame.mouse.get_pos()
        if self.last_pos is None:
            self.last_pos = pos
            return 0.0, 0.0
        if self._modifier_pressed():
            self.last_pos = pos
            return 0.0, 0.0
        dx = pos[0] - self.last_pos[0]
        dy = pos[1] - self.last_pos[1]
        self.last_pos = pos
        x = max(-1.0, min(1.0, dx / self.scale))
        y = max(-1.0, min(1.0, dy / self.scale))
        return x, y
