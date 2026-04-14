import pygame
from config import Cfg


class Button:
    def __init__(self, x, y, w, h, label, color=None,
                 hover_color=None, active_color=None,
                 font_size=13, tooltip=""):
        self.rect         = pygame.Rect(x, y, w, h)
        self.label        = label
        self.color        = color        or Cfg.C_BTN
        self.hover_color  = hover_color  or Cfg.C_BTN_HOVER
        self.active_color = active_color or Cfg.C_BTN_ACTIVE
        self.active       = False
        self.tooltip      = tooltip
        self.font         = pygame.font.SysFont("consolas", font_size, bold=True)
        self._hovered     = False

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        self._hovered = self.rect.collidepoint(mx, my)

        color = self.active_color if self.active else (
            self.hover_color if self._hovered else self.color
        )

        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, Cfg.C_ACCENT, self.rect, 1, border_radius=5)

        lbl = self.font.render(self.label, True, Cfg.C_TEXT)
        screen.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                          self.rect.centery - lbl.get_height()//2))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


class Toggle:
    SIZE = 14

    def __init__(self, x, y, label, initial=True):
        self.x = x
        self.y = y
        self.label = label
        self.value = initial
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.font = pygame.font.SysFont("consolas", 12)

    def draw(self, screen):
        pygame.draw.rect(screen, Cfg.C_BTN, self.rect, border_radius=3)

        if self.value:
            pygame.draw.rect(screen, Cfg.C_ACCENT,
                             self.rect.inflate(-4, -4), border_radius=2)
        else:
            pygame.draw.rect(screen, Cfg.C_PANEL_LINE, self.rect, 1)

        lbl = self.font.render(
            self.label,
            True,
            Cfg.C_TEXT if self.value else Cfg.C_TEXT_DIM
        )
        screen.blit(lbl, (self.x + self.SIZE + 6, self.y))

    def is_clicked(self, event):
        hit = pygame.Rect(self.x, self.y, self.SIZE + 140, self.SIZE + 4)
        if (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and hit.collidepoint(event.pos)):
            self.value = not self.value
            return True
        return False


class Slider:
    H = 8
    KNOB = 12

    def __init__(self, x, y, w, min_val, max_val, initial, label=""):
        self.x = x
        self.y = y
        self.w = w
        self.min = min_val
        self.max = max_val
        self.value = initial
        self.label = label
        self._drag = False
        self.track = pygame.Rect(x, y + 6, w, self.H)
        self.font = pygame.font.SysFont("consolas", 11)

    def _knob_x(self):
        r = (self.value - self.min) / max(1, self.max - self.min)
        return int(self.x + r * self.w)

    def draw(self, screen):
        pygame.draw.rect(screen, Cfg.C_SLIDER_TRACK, self.track, border_radius=4)

        fill = pygame.Rect(self.x, self.track.y,
                           self._knob_x() - self.x, self.H)
        pygame.draw.rect(screen, Cfg.C_ACCENT, fill, border_radius=4)

        kx, ky = self._knob_x(), self.y + 6
        pygame.draw.circle(screen, Cfg.C_SLIDER_KNOB, (kx, ky), 6)

        lbl = self.font.render(f"{self.label}: {self.value}", True, Cfg.C_TEXT)
        screen.blit(lbl, (self.x, self.y - 16))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._drag = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag = False
        elif event.type == pygame.MOUSEMOTION and self._drag:
            rx = max(self.x, min(self.x + self.w, event.pos[0]))
            r = (rx - self.x) / self.w
            self.value = int(self.min + r * (self.max - self.min))
            return True
        return False


class Dropdown:
    ITEM_H = 24

    def __init__(self, x, y, w, options, selected_index=0):
        self.x = x
        self.y = y
        self.w = w
        self.options = options
        self.index = selected_index
        self.open = False
        self.font = pygame.font.SysFont("consolas", 12, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 11)

    @property
    def selected(self):
        return self.options[self.index]

    def draw(self, screen):
        box = pygame.Rect(self.x, self.y, self.w, self.ITEM_H)
        pygame.draw.rect(screen, Cfg.C_BTN_HOVER, box, border_radius=4)
        pygame.draw.rect(screen, Cfg.C_ACCENT, box, 1, border_radius=4)

        lbl = self.font.render(self.selected, True, Cfg.C_ACCENT)
        screen.blit(lbl, (self.x + 8, self.y + 4))

        arrow = "▲" if self.open else "▼"
        arw = self.font_sm.render(arrow, True, Cfg.C_TEXT_DIM)
        screen.blit(arw, (self.x + self.w - 18, self.y + 5))

        if self.open:
            for i, opt in enumerate(self.options):
                r = pygame.Rect(self.x, self.y + (i+1)*self.ITEM_H,
                                self.w, self.ITEM_H)
                col = Cfg.C_BTN_ACTIVE if i == self.index else Cfg.C_BTN
                pygame.draw.rect(screen, col, r)
                pygame.draw.rect(screen, Cfg.C_PANEL_LINE, r, 1)

                t = self.font_sm.render(opt, True, Cfg.C_TEXT)
                screen.blit(t, (r.x+8, r.y+5))

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        box = pygame.Rect(self.x, self.y, self.w, self.ITEM_H)
        if box.collidepoint(event.pos):
            self.open = not self.open
            return False

        if self.open:
            for i in range(len(self.options)):
                r = pygame.Rect(self.x, self.y + (i+1)*self.ITEM_H,
                                self.w, self.ITEM_H)
                if r.collidepoint(event.pos):
                    if self.index != i:
                        self.index = i
                        self.open = False
                        return True
            self.open = False
        return False