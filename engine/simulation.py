"""
engine/simulation.py
─────────────────────
SimEngine — wires every module together.

States
------
IDLE        waiting for Start
PLANNING    running pathfinding (instant)
NAVIGATING  agent following path
REPLANNING  dynamic obstacle hit → recomputing
PAUSED      user pressed Pause
CHECKPOINT  just reached a checkpoint, replanning to next target
REACHED     goal reached
NO_PATH     algorithm found no route
OUT_ENERGY  agent ran out of fuel
COMPARING   running all-algo comparison (blocking, fast)
REPLAYING   playing back a saved run
"""

import time
from config            import Cfg
from engine.environment import GridEnvironment
from engine.agent       import Agent
from engine.recorder    import Recorder, Replayer
from algorithms         import run_algorithm, compare_all
from utils.helpers      import path_length


class SimEngine:
    """Top-level controller.  UI calls methods; render reads state."""

    # ── Init ────────────────────────────────────────────────────────── #
    def __init__(self):
        self.algorithm:    str  = Cfg.ALGORITHMS[0]   # "A*"
        self.status:       str  = "IDLE"
        self.show_heatmap: bool = False
        self.show_fog:     bool = True
        self.show_grid:    bool = True
        self.show_checkpoints: bool = True

        self.env:     GridEnvironment | None = None
        self.agent:   Agent           | None = None
        self.path:    list  = []
        self.visited: set   = set()

        self.comparison_results: dict = {}   # populated by compare_all
        self.elapsed:  float = 0.0
        self._t_start: float = 0.0

        self.recorder = Recorder()
        self.replayer = Replayer()

        self._screenshot_count = 0
        self._plan_time_ms:  float = 0.0
        self._plan_nodes:    int   = 0
        self._plan_length:   float = 0.0

        self.reset()

    # ── Public controls (called by UI buttons) ──────────────────────── #
    def reset(self):
        """Build a fresh environment and agent; stay in IDLE."""
        self.env   = GridEnvironment()
        self.agent = Agent(self.env)
        self.path    = []
        self.visited = set()
        self.status  = "IDLE"
        self.elapsed = 0.0
        self.comparison_results = {}
        self._plan_time_ms = 0.0
        self._plan_nodes   = 0
        self._plan_length  = 0.0
        self.recorder = Recorder()
        print("[ENGINE] Reset complete.")

    def start(self):
        """Plan and begin navigation."""
        if self.status in ("NAVIGATING", "REPLAYING"):
            return
        self._plan()
        if self.path:
            self._t_start = time.time()
            self.status   = "NAVIGATING"
            self.recorder.start()
            print(f"[ENGINE] Navigation started — {self.algorithm}")

    def pause_resume(self):
        if self.status == "NAVIGATING":
            self.agent.paused = True
            self.status = "PAUSED"
        elif self.status == "PAUSED":
            self.agent.paused = False
            self.status = "NAVIGATING"

    def compare(self):
        """Run all algorithms and store comparison results."""
        print("[ENGINE] Running comparison...")
        prev_status = self.status
        self.status = "COMPARING"
        self.comparison_results = compare_all(
            self.env,
            self.agent.cell,
            self.env.goal,
        )
        self.status = prev_status if prev_status != "COMPARING" else "IDLE"
        print("[ENGINE] Comparison done.")

    def save_run(self) -> str:
        if not self.recorder.positions:
            return ""
        self.recorder.stop(
            self.algorithm,
            self.agent.steps_taken,
            self.agent.distance_travelled,
            self._plan_length,
            self.agent.replans,
        )
        fname = self.recorder.save()
        print(f"[ENGINE] Run saved: {fname}")
        return fname

    def start_replay(self) -> bool:
        ok = self.replayer.load_latest()
        if ok:
            self.status = "REPLAYING"
            print(f"[ENGINE] Replaying: {self.replayer.metadata}")
        else:
            print("[ENGINE] No replay found. Save a run first.")
        return ok

    def set_algorithm(self, name: str):
        if name in Cfg.ALGORITHMS:
            self.algorithm = name
            print(f"[ENGINE] Algorithm → {name}")

    def set_speed(self, value: int):
        """value from slider: 1..30 (lower = faster)"""
        if self.agent:
            self.agent.speed = max(Cfg.AGENT_SPEED_MIN,
                                   min(Cfg.AGENT_SPEED_MAX, value))

    # ── Per-frame update ────────────────────────────────────────────── #
    def update(self):
        """Call once per frame from the main loop."""
        if self.status == "REPLAYING":
            self._update_replay()
            return

        if self.status not in ("NAVIGATING", "REPLANNING"):
            return

        self.elapsed = time.time() - self._t_start

        # Move dynamic obstacles
        self.env.update_dynamic_obstacles()

        # Record position
        self.recorder.record(self.agent.row, self.agent.col)

        # Update agent
        needs_replan = self.agent.update(self.env.dynamic_obstacle_cells())

        # Agent ran out of energy
        if self.agent.out_of_energy:
            self.status = "OUT_ENERGY"
            print("[ENGINE] Out of energy!")
            return

        # Just cleared a checkpoint → plan to next target
        if not self.agent.path and not self.agent.reached_goal \
                and not self.agent.out_of_energy:
            self.status = "CHECKPOINT"
            print(f"[ENGINE] Checkpoint reached! Next: {self.agent.current_target}")
            self._plan()
            if self.path:
                self.status = "NAVIGATING"
            else:
                self.status = "NO_PATH"
            return

        # Dynamic obstacle detected → replan
        if needs_replan and self.status == "NAVIGATING":
            self.status = "REPLANNING"
            self._plan()
            if self.path:
                self.status = "NAVIGATING"
            else:
                self.status = "NO_PATH"
            return

        # Goal reached
        if self.agent.reached_goal:
            self.status = "REACHED"
            print(f"[ENGINE] GOAL REACHED in {self.elapsed:.2f}s  "
                  f"steps={self.agent.steps_taken}  "
                  f"replans={self.agent.replans}")

    # ── Replay update ────────────────────────────────────────────────── #
    def _update_replay(self):
        pos = self.replayer.current_pos()
        if pos:
            self.agent.row = pos[0]
            self.agent.col = pos[1]
            self.replayer.advance()
        else:
            self.status = "IDLE"
            print("[ENGINE] Replay finished.")

    # ── Internal planner ─────────────────────────────────────────────── #
    def _plan(self):
        """Run selected algorithm from agent's current cell to current target."""
        start  = self.agent.cell
        target = self.agent.current_target
        path, visited, ms = run_algorithm(self.algorithm,
                                          self.env, start, target)
        self.visited = visited
        self.env.record_visit(visited)

        if path:
            self.path           = path
            self._plan_time_ms  = ms
            self._plan_nodes    = len(visited)
            self._plan_length   = path_length(path)
            self.agent.set_path(path)
            print(f"[{self.algorithm}] {len(path)} wpts | "
                  f"len={self._plan_length} | "
                  f"explored={len(visited)} | {ms}ms")
        else:
            self.path  = []
            self.status = "NO_PATH"
            print(f"[{self.algorithm}] No path from {start} to {target}")

    # ── Screenshot helper ────────────────────────────────────────────── #
    def next_screenshot_name(self) -> str:
        import os
        os.makedirs(Cfg.SCREENSHOT_DIR, exist_ok=True)
        name = f"{Cfg.SCREENSHOT_DIR}/shot_{self._screenshot_count:03d}.png"
        self._screenshot_count += 1
        return name
