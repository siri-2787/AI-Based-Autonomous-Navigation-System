import pygame
from config import Cfg


class HUD:
    def __init__(self):
        pygame.font.init()

        # Fonts
        self.f_title = pygame.font.SysFont("consolas", 13, bold=True)
        self.f_label = pygame.font.SysFont("consolas", 11, bold=True)
        self.f_value = pygame.font.SysFont("consolas", 11)
        self.f_tiny  = pygame.font.SysFont("consolas", 10, bold=True)

    # ─────────────────────────────────────────────
    def draw(self, screen, engine, py_start):
        px = Cfg.GRID_COLS * Cfg.CELL_SIZE + 10
        y = py_start

        y = self._section(screen, px, y, "Agent Metrics")
        y = self._live_stats(screen, px, y, engine)

        if engine.comparison_results:
            y += 6
            y = self._section(screen, px, y, "Algorithm Analysis")
            y = self._comparison_table(
                screen, px, y,
                engine.comparison_results,
                engine.algorithm
            )

        if engine.status == "REPLAYING":
            y += 6
            y = self._section(screen, px, y, "Replay Info")
            y = self._replay_info(screen, px, y, engine.replayer)

    # ─────────────────────────────────────────────
    def _section(self, screen, px, y, title):
        """Stylized section header"""
        t = self.f_title.render(title, True, Cfg.C_ACCENT)
        screen.blit(t, (px, y))

        y += t.get_height() + 3

        # glowing separator line (UI upgrade)
        pygame.draw.line(
            screen,
            Cfg.C_PANEL_LINE,
            (px, y),
            (px + Cfg.PANEL_W - 20, y),
            2
        )
        return y + 6

    # ─────────────────────────────────────────────
    def _row(self, screen, px, y, label, value, col=None):
        """Aligned key-value row"""
        l = self.f_label.render(label, True, Cfg.C_TEXT_DIM)
        v = self.f_value.render(value, True, col or Cfg.C_TEXT)

        screen.blit(l, (px, y))
        screen.blit(v, (px + 110, y))  # better spacing than 90

        return y + 15

    # ─────────────────────────────────────────────
    def _calc_efficiency(self, engine):
        """
        Efficiency formula (balanced scoring):

        lower time + fewer steps + fewer explored nodes => higher score
        """

        ag = engine.agent

        time_cost = max(0.1, engine.elapsed)
        path_cost = max(1, ag.distance_travelled)
        explore_cost = max(1, engine._plan_nodes)
        replans = max(1, ag.replans)

        # weighted cost model
        cost = (
            0.45 * time_cost +
            0.30 * path_cost +
            0.15 * explore_cost +
            0.10 * replans
        )

        score = 1 / cost

        # normalize to 0–1 range (UI friendly)
        return max(0.0, min(1.0, score * 12))

    # ─────────────────────────────────────────────
    def _live_stats(self, screen, px, y, engine):
        ag = engine.agent

        y = self._row(screen, px, y, "STATUS", engine.status)

        if engine.algorithm:
            y = self._row(
                screen, px, y,
                "MODE",
                engine.algorithm,
                Cfg.C_ACCENT
            )

        y = self._row(screen, px, y, "STEPS", str(ag.steps_taken))
        y = self._row(screen, px, y, "DIST", f"{ag.distance_travelled:.1f}")
        y = self._row(screen, px, y, "REPLANS", str(ag.replans))
        y = self._row(screen, px, y, "TIME", f"{engine.elapsed:.1f}s")

        # ⭐ NEW: Efficiency Score
        eff = self._calc_efficiency(engine)

        eff_color = (
            (0, 255, 180) if eff > 0.7
            else (255, 200, 0) if eff > 0.4
            else Cfg.C_WARN
        )

        y = self._row(
            screen,
            px,
            y,
            "EFFICIENCY",
            f"{eff:.3f}",
            eff_color
        )

        return y

    # ─────────────────────────────────────────────
    def _comparison_table(self, screen, px, y, results, active):

    # ── HEADER ROW (NEW) ─────────────────────────────
        header = self.f_tiny.render("Algorithm   Time(ms)   Nodes", True, Cfg.C_TEXT)
        screen.blit(header, (px, y))
        y += 14

        pygame.draw.line(
        screen,
        Cfg.C_PANEL_LINE,
        (px, y),
        (px + Cfg.PANEL_W - 16, y)
        )
        y += 6

    # ── DATA ROWS ────────────────────────────────────
        for algo, data in results.items():
            col = Cfg.C_ACCENT if algo == active else Cfg.C_TEXT_DIM

            time_ms = data.get("time_ms", 0)

            # safe fallback for nodes/explored
            nodes = data.get("nodes", data.get("explored", 0))

            txt = f"{algo[:6]:<10} {time_ms:>6.1f}   {nodes:>6}"
            t = self.f_tiny.render(txt, True, col)
            screen.blit(t, (px, y))
            y += 12

        return y    
    # ─────────────────────────────────────────────
    def _replay_info(self, screen, px, y, r):
        m = r.metadata
        if not m:
            return y

        y = self._row(screen, px, y, "ALGO", m.get("algorithm", "?"))
        y = self._row(screen, px, y, "STEPS", str(m.get("steps", "?")))
        y = self._row(screen, px, y, "DIST", str(m.get("distance", "?")))

        # replay progress
        progress = (
            r.index / max(1, len(r.positions))
            if hasattr(r, "positions") else 0
        )

        y = self._row(
            screen,
            px,
            y,
            "PROGRESS",
            f"{int(progress * 100)}%",
            Cfg.C_ACCENT
        )

        return y