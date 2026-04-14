"""
engine/environment.py
─────────────────────
Grid world with:
  • Static obstacles (randomly generated)
  • Dynamic (moving) obstacles that bounce
  • Checkpoints the agent must visit
  • Fog-of-war reveal tracking
"""

import random
import math
from config import Cfg


class GridEnvironment:
    """
    2-D grid world.  Cell values:  0 = free,  1 = static obstacle.
    """

    def __init__(self):
        self.rows             = Cfg.GRID_ROWS
        self.cols             = Cfg.GRID_COLS
        self.obstacle_density = Cfg.OBSTACLE_DENSITY
        self.start            = (1, 1)
        self.goal             = (self.rows - 2, self.cols - 2)

        self.grid              = []
        self.dynamic_obstacles = []   # list of {row, col, vr, vc}
        self.checkpoints       = []   # list of (r,c) in visit order
        self.revealed          = set()  # cells seen by agent (fog of war)
        self.heat_map          = {}     # (r,c) → visit count (for heatmap)

        self.reset()

    # ── Full reset ─────────────────────────────────────────────────── #
    def reset(self):
        self._generate_grid()
        self._place_dynamic_obstacles()
        self._place_checkpoints()
        self._init_fog()
        self.heat_map = {}

    # ── Map generation ─────────────────────────────────────────────── #
    def _generate_grid(self):
        """Random grid with border walls and interior obstacles."""
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows-1 or c == 0 or c == self.cols-1:
                    self.grid[r][c] = 1
                elif random.random() < self.obstacle_density:
                    self.grid[r][c] = 1

        # Clear zones around start, goal
        for dr in range(-1, 3):
            for dc in range(-1, 3):
                for base in [self.start, self.goal]:
                    nr, nc = base[0]+dr, base[1]+dc
                    if self._valid(nr, nc):
                        self.grid[nr][nc] = 0

    # ── Dynamic obstacles ──────────────────────────────────────────── #
    def _place_dynamic_obstacles(self):
        """Scatter moving obstacles at random free cells."""
        self.dynamic_obstacles = []
        reserved = {self.start, self.goal}
        placed, attempts = 0, 0
        while placed < Cfg.DYN_OBS_COUNT and attempts < 5000:
            attempts += 1
            r = random.randint(3, self.rows - 4)
            c = random.randint(3, self.cols - 4)
            if self.grid[r][c] == 0 and (r, c) not in reserved:
                angle = random.uniform(0, 2 * math.pi)
                self.dynamic_obstacles.append({
                    "row": float(r), "col": float(c),
                    "vr":  math.sin(angle) * Cfg.DYN_OBS_SPEED,
                    "vc":  math.cos(angle) * Cfg.DYN_OBS_SPEED,
                })
                placed += 1

    def update_dynamic_obstacles(self):
        """Move each dynamic obstacle; bounce off walls."""
        for obs in self.dynamic_obstacles:
            nr = obs["row"] + obs["vr"]
            nc = obs["col"] + obs["vc"]
            if nr < 1 or nr >= self.rows - 1:
                obs["vr"] *= -1; nr = obs["row"] + obs["vr"]
            if nc < 1 or nc >= self.cols - 1:
                obs["vc"] *= -1; nc = obs["col"] + obs["vc"]
            ir, ic = int(nr), int(nc)
            if self._valid(ir, ic) and self.grid[ir][ic] == 1:
                obs["vr"] *= -1; obs["vc"] *= -1
                nr = obs["row"] + obs["vr"]
                nc = obs["col"] + obs["vc"]
            obs["row"] = nr
            obs["col"] = nc

    def dynamic_obstacle_cells(self) -> set:
        return {(int(o["row"]), int(o["col"])) for o in self.dynamic_obstacles}

    # ── Checkpoints ────────────────────────────────────────────────── #
    def _place_checkpoints(self):
        """Place N checkpoints at random free cells."""
        self.checkpoints = []
        reserved = {self.start, self.goal}
        attempts = 0
        while len(self.checkpoints) < Cfg.CHECKPOINT_COUNT and attempts < 5000:
            attempts += 1
            r = random.randint(2, self.rows - 3)
            c = random.randint(2, self.cols - 3)
            cell = (r, c)
            if self.grid[r][c] == 0 and cell not in reserved \
                    and cell not in self.checkpoints:
                self.checkpoints.append(cell)
                reserved.add(cell)

    # ── Fog of War ─────────────────────────────────────────────────── #
    def _init_fog(self):
        """Reveal cells near start at the beginning."""
        self.revealed = set()
        self.reveal_around(self.start[0], self.start[1], Cfg.SENSOR_RADIUS)

    def reveal_around(self, row: float, col: float, radius: int):
        """Mark all cells within radius of (row,col) as revealed."""
        ir, ic = int(round(row)), int(round(col))
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if dr*dr + dc*dc <= radius*radius:
                    nr, nc = ir + dr, ic + dc
                    if self._valid(nr, nc):
                        self.revealed.add((nr, nc))

    # ── Heat map ────────────────────────────────────────────────────── #
    def record_visit(self, visited: set):
        """Accumulate A* visited nodes into the heat map."""
        for cell in visited:
            self.heat_map[cell] = self.heat_map.get(cell, 0) + 1

    # ── Helpers ─────────────────────────────────────────────────────── #
    def _valid(self, r, c) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_free(self, r, c) -> bool:
        return self._valid(r, c) and self.grid[r][c] == 0

    def neighbors(self, r: int, c: int) -> list:
        """8-connected walkable neighbours."""
        result = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),
                       (-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r+dr, c+dc
            if self.is_free(nr, nc):
                if dr != 0 and dc != 0:
                    if not self.is_free(r+dr, c) or not self.is_free(r, c+dc):
                        continue
                result.append((nr, nc))
        return result
