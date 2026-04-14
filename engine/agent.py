"""
engine/agent.py
───────────────
Autonomous agent with:
  • Smooth sub-cell interpolation
  • Energy / fuel system
  • Checkpoint tracking
  • Proximity sensor (triggers replan)
  • Fog-of-war reveal on every step
"""

import math
from config import Cfg


class Agent:
    """
    The robot navigating the grid.
    Follows a waypoint path with smooth interpolation.
    """

    def __init__(self, env):
        self.env    = env
        self.start  = env.start
        self.goal   = env.goal
        self.speed  = Cfg.AGENT_SPEED_DEFAULT  # frames per cell

        # Float position for smooth animation
        self.row = float(self.start[0])
        self.col = float(self.start[1])

        # Path
        self.path:       list  = []
        self.path_index: int   = 0
        self._progress:  int   = 0

        # Energy
        self.energy:     float = Cfg.MAX_ENERGY
        self.out_of_energy: bool = False

        # Checkpoints — copy from env, track which are completed
        self.checkpoints_remaining: list = list(env.checkpoints)
        self.checkpoints_done:      list = []

        # State flags
        self.paused:       bool = False
        self.reached_goal: bool = False

        # Metrics
        self.steps_taken:        int   = 0
        self.distance_travelled: float = 0.0
        self.replans:            int   = 0

        # Replay recording: list of (row, col) snapshots
        self.position_log: list = []

    # ── Path assignment ─────────────────────────────────────────────── #
    def set_path(self, path: list):
        """Set a fresh path (called at start or after replan)."""
        self.path        = path
        self.path_index  = 1
        self._progress   = 0

    def replan(self, new_path: list):
        """Accept a new path from the replanner."""
        if new_path:
            self.path        = new_path
            self.path_index  = 1
            self._progress   = 0
            self.replans    += 1

    # ── Per-frame update ────────────────────────────────────────────── #
    def update(self, dynamic_obs_cells: set) -> bool:
        """
        Advance one frame.
        Returns True  → replan needed.
        Returns False → all good.
        """
        if self.paused or self.reached_goal or self.out_of_energy:
            return False
        if not self.path or self.path_index >= len(self.path):
            # Arrived at current target
            self._check_target_reached()
            return False

        target_r, target_c = self.path[self.path_index]
        prev_r = self.path[self.path_index - 1][0]
        prev_c = self.path[self.path_index - 1][1]

        # ── Smooth interpolation ────────────────────────────────────
        self._progress += 1
        t        = self._progress / self.speed
        self.row = prev_r + t * (target_r - prev_r)
        self.col = prev_c + t * (target_c - prev_c)

        # ── Arrived at waypoint ─────────────────────────────────────
        if self._progress >= self.speed:
            self.row        = float(target_r)
            self.col        = float(target_c)
            self.path_index += 1
            self._progress  = 0
            self.steps_taken += 1

            # Energy cost
            dr  = target_r - prev_r
            dc  = target_c - prev_c
            dist = math.sqrt(dr*dr + dc*dc)
            self.distance_travelled += dist
            self.energy = max(0.0, self.energy - dist)
            if self.energy <= 0.0:
                self.out_of_energy = True
                return False

            # Fog reveal
            self.env.reveal_around(self.row, self.col, Cfg.SENSOR_RADIUS)

            # Log position for replay
            self.position_log.append((self.row, self.col))

            # Check checkpoint / goal
            self._check_target_reached()

        # ── Obstacle sensor ─────────────────────────────────────────
        return self._obstacle_ahead(dynamic_obs_cells)

    # ── Target checking ─────────────────────────────────────────────── #
    def _check_target_reached(self):
        cell = self.cell

        # Checkpoint?
        if self.checkpoints_remaining and \
                cell == self.checkpoints_remaining[0]:
            done = self.checkpoints_remaining.pop(0)
            self.checkpoints_done.append(done)
            # Signal caller that we need a new path to next target
            self.path = []

        # Goal?
        elif cell == self.goal and not self.checkpoints_remaining:
            self.reached_goal = True

    @property
    def current_target(self) -> tuple:
        """Next waypoint target: next checkpoint or final goal."""
        if self.checkpoints_remaining:
            return self.checkpoints_remaining[0]
        return self.goal

    # ── Sensor ──────────────────────────────────────────────────────── #
    def _obstacle_ahead(self, dynamic_obs_cells: set) -> bool:
        """Return True if a dynamic obstacle is on an upcoming path cell."""
        look_ahead = Cfg.SENSOR_RADIUS + 1
        end = min(self.path_index + look_ahead, len(self.path))
        for i in range(self.path_index, end):
            if self.path[i] in dynamic_obs_cells:
                return True
        return False

    # ── Properties ──────────────────────────────────────────────────── #
    @property
    def cell(self) -> tuple:
        return (int(round(self.row)), int(round(self.col)))

    @property
    def energy_pct(self) -> float:
        return self.energy / Cfg.MAX_ENERGY

    def reset(self):
        self.__init__(self.env)
