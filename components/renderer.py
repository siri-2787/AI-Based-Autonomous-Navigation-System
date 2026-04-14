"""
components/renderer.py
───────────────────────
Draws the grid world: cells, heatmap, fog, path, obstacles, agent.
No game logic — pure drawing.
"""

import pygame
import math
from config import Cfg


class Renderer:
    """Draws the grid area on the left portion of the screen."""

    def __init__(self):
        pygame.font.init()
        self.f_cell = pygame.font.SysFont("consolas", 9)

    # ── Master draw call ────────────────────────────────────────────── #
    def draw_world(self, screen: pygame.Surface, engine):
        """Draw everything inside the grid area."""
        env   = engine.env
        agent = engine.agent

        self._draw_cells(screen, env, engine.visited,
                         engine.show_heatmap, engine.show_fog)

        if engine.show_grid:
            self._draw_grid_lines(screen, env.rows, env.cols)

        self._draw_path(screen, engine.path,
                        Cfg.ALGO_COLORS.get(engine.algorithm, Cfg.C_PATH))

        if engine.show_checkpoints:
            self._draw_checkpoints(screen, agent)

        self._draw_start_goal(screen, env.start, env.goal)
        self._draw_dynamic_obstacles(screen, env.dynamic_obstacles,
                                     engine.show_fog, env.revealed)

        self._draw_sensor_ring(screen, agent)
        self._draw_agent(screen, agent, engine.status)

    # ── Cells ───────────────────────────────────────────────────────── #
    def _draw_cells(self, screen, env, visited: set,
                    heatmap: bool, fog: bool):
        cs   = Cfg.CELL_SIZE
        rows = env.rows
        cols = env.cols

        # Precompute heat max for normalisation
        heat_max = max(env.heat_map.values(), default=1)

        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c*cs, r*cs, cs, cs)
                cell = (r, c)

                # Fog of war: hide unrevealed cells
                if fog and cell not in env.revealed:
                    pygame.draw.rect(screen, Cfg.C_FOG, rect)
                    continue

                if env.grid[r][c] == 1:
                    pygame.draw.rect(screen, Cfg.C_WALL, rect)

                elif heatmap and cell in env.heat_map:
                    intensity = env.heat_map[cell] / heat_max
                    color = self._heat_color(intensity)
                    pygame.draw.rect(screen, color, rect)

                elif cell in visited:
                    pygame.draw.rect(screen, Cfg.C_EXPLORED, rect)

                else:
                    pygame.draw.rect(screen, Cfg.C_FREE, rect)

    def _heat_color(self, t: float) -> tuple:
        """Interpolate across the heatmap palette."""
        palette = Cfg.HEAT_COLORS
        n       = len(palette) - 1
        i       = min(int(t * n), n - 1)
        lt      = t * n - i
        c0, c1  = palette[i], palette[i+1]
        return tuple(int(c0[k] + lt * (c1[k] - c0[k])) for k in range(3))

    # ── Grid lines ──────────────────────────────────────────────────── #
    def _draw_grid_lines(self, screen, rows, cols):
        cs = Cfg.CELL_SIZE
        for r in range(rows + 1):
            pygame.draw.line(screen, Cfg.C_GRID, (0, r*cs), (cols*cs, r*cs))
        for c in range(cols + 1):
            pygame.draw.line(screen, Cfg.C_GRID, (c*cs, 0), (c*cs, rows*cs))

    # ── Path ────────────────────────────────────────────────────────── #
    def _draw_path(self, screen, path: list, color):
        if len(path) < 2:
            return
        cs  = Cfg.CELL_SIZE
        pts = [(int(c*cs + cs//2), int(r*cs + cs//2)) for r, c in path]
        pygame.draw.lines(screen, color, False, pts, 3)
        for px, py in pts:
            pygame.draw.circle(screen, color, (px, py), 3)

    # ── Checkpoints ─────────────────────────────────────────────────── #
    def _draw_checkpoints(self, screen, agent):
        cs = Cfg.CELL_SIZE
        for i, (r, c) in enumerate(agent.checkpoints_remaining):
            cx   = c*cs + cs//2
            cy   = r*cs + cs//2
            half = cs//2 - 2
            # Star shape (octagon)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                px  = cx + int(half * math.cos(rad))
                py  = cy + int(half * math.sin(rad))
                pygame.draw.circle(screen, Cfg.C_CHECKPOINT, (px, py), 3)
            pygame.draw.circle(screen, Cfg.C_CHECKPOINT, (cx, cy), 5)
            # Number label
            lbl = self.f_cell.render(str(i+1), True, (0,0,0))
            screen.blit(lbl, (cx-3, cy-4))

        for r, c in agent.checkpoints_done:
            cx = c*cs + cs//2
            cy = r*cs + cs//2
            pygame.draw.circle(screen, Cfg.C_CHECKPOINT_DONE, (cx, cy), 5)
            pygame.draw.circle(screen, (255,255,255), (cx, cy), 5, 1)

    # ── Start / Goal ────────────────────────────────────────────────── #
    def _draw_start_goal(self, screen, start, goal):
        cs = Cfg.CELL_SIZE
        s  = cs - 4

        # Start — yellow square with S
        sr = pygame.Rect(start[1]*cs+2, start[0]*cs+2, s, s)
        pygame.draw.rect(screen, Cfg.C_START, sr, border_radius=3)
        lbl = self.f_cell.render("S", True, (0,0,0))
        screen.blit(lbl, (start[1]*cs + cs//2 - 3, start[0]*cs + cs//2 - 4))

        # Goal — pink diamond
        cx = goal[1]*cs + cs//2
        cy = goal[0]*cs + cs//2
        half = cs//2 - 2
        pts  = [(cx, cy-half),(cx+half, cy),(cx, cy+half),(cx-half, cy)]
        pygame.draw.polygon(screen, Cfg.C_GOAL, pts)
        lbl = self.f_cell.render("G", True, (0,0,0))
        screen.blit(lbl, (cx-3, cy-4))

    # ── Dynamic obstacles ───────────────────────────────────────────── #
    def _draw_dynamic_obstacles(self, screen, dynamic_obstacles,
                                fog: bool, revealed: set):
        cs = Cfg.CELL_SIZE
        for obs in dynamic_obstacles:
            ir, ic = int(obs["row"]), int(obs["col"])
            if fog and (ir, ic) not in revealed:
                continue
            cx = int(obs["col"]*cs + cs//2)
            cy = int(obs["row"]*cs + cs//2)
            r  = cs//2 - 2

            # Glow
            gs = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*Cfg.C_DYN_OBS, 55), (r*2, r*2), r*2)
            screen.blit(gs, (cx - r*2, cy - r*2))

            # Body
            pygame.draw.circle(screen, Cfg.C_DYN_OBS, (cx, cy), r)
            # X
            pygame.draw.line(screen, (255,255,255),
                             (cx-4, cy-4), (cx+4, cy+4), 2)
            pygame.draw.line(screen, (255,255,255),
                             (cx+4, cy-4), (cx-4, cy+4), 2)

    # ── Sensor ring ─────────────────────────────────────────────────── #
    def _draw_sensor_ring(self, screen, agent):
        cs     = Cfg.CELL_SIZE
        cx     = int(agent.col*cs + cs//2)
        cy     = int(agent.row*cs + cs//2)
        radius = int(Cfg.SENSOR_RADIUS * cs)
        surf   = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*Cfg.C_AGENT, 20), (radius+2, radius+2), radius)
        pygame.draw.circle(surf, (*Cfg.C_AGENT, 70), (radius+2, radius+2), radius, 1)
        screen.blit(surf, (cx-radius-2, cy-radius-2))

    # ── Agent ───────────────────────────────────────────────────────── #
    def _draw_agent(self, screen, agent, status: str):
        cs = Cfg.CELL_SIZE
        cx = int(agent.col*cs + cs//2)
        cy = int(agent.row*cs + cs//2)
        r  = cs//2 - 2

        # Pulsing outer ring when replanning
        if status == "REPLANNING":
            t  = pygame.time.get_ticks() % 500 / 500
            pr = int(r + 4 + t * 4)
            ps = pygame.Surface((pr*2+4, pr*2+4), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*Cfg.C_WARN, 80), (pr+2, pr+2), pr, 2)
            screen.blit(ps, (cx-pr-2, cy-pr-2))

        # Body
        color = Cfg.C_DANGER if agent.out_of_energy else Cfg.C_AGENT
        pygame.draw.circle(screen, color, (cx, cy), r)
        pygame.draw.circle(screen, (255,255,255), (cx, cy), r, 2)

        # Direction arrow
        if agent.path and agent.path_index < len(agent.path):
            nr, nc = agent.path[agent.path_index]
            angle  = math.atan2(nr - agent.row, nc - agent.col)
            tip_x  = cx + int(r * math.cos(angle))
            tip_y  = cy + int(r * math.sin(angle))
            pygame.draw.line(screen, (0,0,0), (cx, cy), (tip_x, tip_y), 3)
