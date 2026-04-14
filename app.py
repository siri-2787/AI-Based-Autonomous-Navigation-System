import pygame

from config import Cfg
from engine.simulation import SimEngine
from components.renderer import Renderer
from components.hud import HUD
from components.controls import Button, Toggle, Slider, Dropdown


class App:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((Cfg.WIN_W, Cfg.WIN_H))
        pygame.display.set_caption(Cfg.TITLE)
        self.clock = pygame.time.Clock()

        self.engine = SimEngine()
        self.renderer = Renderer()
        self.hud = HUD()

        self.PX = Cfg.GRID_COLS * Cfg.CELL_SIZE

        self._build_controls()

    # ───────────────────────────────────────────── #
    def _build_controls(self):
        px = self.PX + 10
        y = 12

        # ── Dropdown label ──
        self._lbl_algo_y = y
        y += 16

        self.dd_algo = Dropdown(
            px, y,
            Cfg.PANEL_W - 20,
            Cfg.ALGORITHMS,
            selected_index=0
        )
        y += 30

        # ── Buttons (UI upgraded text) ──
        BW, BH, GAP = 118, 28, 8

        self.btn_start = Button(px, y, BW, BH, "▶ Run Navigation")
        self.btn_pause = Button(px + BW + GAP, y, BW, BH, "⏸ Pause Agent")
        y += BH + GAP

        self.btn_reset = Button(px, y, BW, BH, "🔄 New Environment")
        self.btn_compare = Button(px + BW + GAP, y, BW, BH, "⚡ Benchmark Algorithms")
        y += BH + GAP

        self.btn_save = Button(px, y, BW, BH, "💾 Save Simulation")
        self.btn_replay = Button(px + BW + GAP, y, BW, BH, "▶ Replay Run")
        y += BH + GAP

        self.btn_shot = Button(px, y, BW * 2 + GAP, BH, "📸 Capture Frame")
        y += BH + 14

        # ── Slider ──
        self.slider_speed = Slider(
            px, y + 18,
            Cfg.PANEL_W - 20,
            Cfg.AGENT_SPEED_MIN,
            Cfg.AGENT_SPEED_MAX,
            Cfg.AGENT_SPEED_DEFAULT,
            label="Speed Control"
        )
        y += 55

        # ── Toggles ──
        self.tog_grid = Toggle(px, y, "Grid Lines", True)
        self.tog_fog = Toggle(px + 135, y, "Fog Mode", True)
        y += 22

        self.tog_heat = Toggle(px, y, "Heatmap", False)
        self.tog_chk = Toggle(px + 135, y, "Checkpoints", True)
        y += 30

        self._hud_start_y = y

        self._buttons = [
            self.btn_start, self.btn_pause, self.btn_reset,
            self.btn_compare, self.btn_save,
            self.btn_replay, self.btn_shot
        ]

    # ───────────────────────────────────────────── #
    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.btn_start.is_clicked(event):
                    self.engine.start()

                if self.btn_pause.is_clicked(event):
                    self.engine.pause_resume()
                    self.btn_pause.active = (self.engine.status == "PAUSED")

                if self.btn_reset.is_clicked(event):
                    self.engine.reset()

                if self.btn_compare.is_clicked(event):
                    self.engine.compare()

                if self.btn_save.is_clicked(event):
                    self.engine.save_run()

                if self.btn_replay.is_clicked(event):
                    self.engine.start_replay()

                if self.btn_shot.is_clicked(event):
                    pygame.image.save(
                        self.screen,
                        self.engine.next_screenshot_name()
                    )

                if self.dd_algo.handle_event(event):
                    self.engine.set_algorithm(self.dd_algo.selected)

                if self.slider_speed.handle_event(event):
                    self.engine.set_speed(self.slider_speed.value)

                if self.tog_grid.is_clicked(event):
                    self.engine.show_grid = self.tog_grid.value

                if self.tog_fog.is_clicked(event):
                    self.engine.show_fog = self.tog_fog.value

                if self.tog_heat.is_clicked(event):
                    self.engine.show_heatmap = self.tog_heat.value

                if self.tog_chk.is_clicked(event):
                    self.engine.show_checkpoints = self.tog_chk.value

            self.engine.update()
            self._render()

            pygame.display.flip()
            self.clock.tick(Cfg.FPS)

        pygame.quit()

    # ───────────────────────────────────────────── #
    def _render(self):
        self.screen.fill(Cfg.C_BG)

        self.renderer.draw_world(self.screen, self.engine)

        panel = pygame.Rect(self.PX, 0, Cfg.PANEL_W, Cfg.WIN_H)
        pygame.draw.rect(self.screen, Cfg.C_PANEL_BG, panel)

        # label
        font = pygame.font.SysFont("consolas", 10, bold=True)
        lbl = font.render("Navigation Strategy", True, Cfg.C_TEXT_DIM)
        self.screen.blit(lbl, (self.PX + 10, self._lbl_algo_y))

        self.dd_algo.draw(self.screen)

        for b in self._buttons:
            b.draw(self.screen)

        self.slider_speed.draw(self.screen)

        self.tog_grid.draw(self.screen)
        self.tog_fog.draw(self.screen)
        self.tog_heat.draw(self.screen)
        self.tog_chk.draw(self.screen)

        self.hud.draw(self.screen, self.engine, self._hud_start_y)