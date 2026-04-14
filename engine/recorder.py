"""
engine/recorder.py
──────────────────
Save a navigation run to JSON and replay it frame-by-frame.
"""

import json
import os
import time
from config import Cfg


class Recorder:
    """Captures agent position snapshots during a run."""

    def __init__(self):
        self.positions: list = []   # [(row, col), ...]
        self.metadata:  dict = {}
        self.recording: bool = False

    def start(self):
        self.positions = []
        self.recording = True

    def record(self, row: float, col: float):
        if self.recording:
            self.positions.append((round(row, 3), round(col, 3)))

    def stop(self, algorithm: str, steps: int, distance: float,
             path_length: float, replans: int):
        self.recording = False
        self.metadata = {
            "algorithm": algorithm,
            "steps":     steps,
            "distance":  round(distance, 2),
            "path_len":  round(path_length, 2),
            "replans":   replans,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def save(self) -> str:
        os.makedirs(Cfg.REPLAY_DIR, exist_ok=True)
        fname = os.path.join(
            Cfg.REPLAY_DIR,
            f"run_{time.strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(fname, "w") as f:
            json.dump({"metadata": self.metadata,
                       "positions": self.positions}, f)
        return fname


class Replayer:
    """Plays back a saved run from a JSON file."""

    def __init__(self):
        self.positions: list  = []
        self.metadata:  dict  = {}
        self.index:     int   = 0
        self.active:    bool  = False
        self.finished:  bool  = False
        self._frame_counter: int = 0
        self.speed: int = 4   # frames to wait between positions

    def load(self, filepath: str) -> bool:
        try:
            with open(filepath) as f:
                data = json.load(f)
            self.positions = [tuple(p) for p in data["positions"]]
            self.metadata  = data.get("metadata", {})
            self.index     = 0
            self.active    = True
            self.finished  = False
            self._frame_counter = 0
            return True
        except Exception as e:
            print(f"[REPLAY] Load failed: {e}")
            return False

    def load_latest(self) -> bool:
        """Load the most recently saved replay file."""
        if not os.path.isdir(Cfg.REPLAY_DIR):
            return False
        files = sorted(
            [f for f in os.listdir(Cfg.REPLAY_DIR) if f.endswith(".json")],
            reverse=True
        )
        if not files:
            return False
        return self.load(os.path.join(Cfg.REPLAY_DIR, files[0]))

    def current_pos(self) -> tuple | None:
        """Return current replay position, or None if done."""
        if not self.active or self.finished:
            return None
        if self.index >= len(self.positions):
            self.finished = True
            return None
        return self.positions[self.index]

    def advance(self):
        """Advance to next position (call every N frames)."""
        self._frame_counter += 1
        if self._frame_counter >= self.speed:
            self._frame_counter = 0
            self.index += 1
            if self.index >= len(self.positions):
                self.finished = True

    def list_replays(self) -> list:
        if not os.path.isdir(Cfg.REPLAY_DIR):
            return []
        return sorted(
            [f for f in os.listdir(Cfg.REPLAY_DIR) if f.endswith(".json")],
            reverse=True
        )[:5]   # show last 5
