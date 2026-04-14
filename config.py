"""
config.py — Single source of truth (FIXED + compatible with renderer)
"""

class Cfg:
    # ── Window ─────────────────────────────
    TITLE        = "AI-Based Autonomous Navigation System"
    GRID_COLS    = 36
    GRID_ROWS    = 28
    CELL_SIZE    = 20
    PANEL_W      = 290
    WIN_W        = GRID_COLS * CELL_SIZE + PANEL_W
    WIN_H        = GRID_ROWS * CELL_SIZE
    FPS          = 60

    # ── World ───────────────────────────────
    OBSTACLE_DENSITY = 0.17
    DYN_OBS_COUNT    = 6
    DYN_OBS_SPEED    = 0.07
    CHECKPOINT_COUNT = 2
    MAX_ENERGY       = 350.0
    SENSOR_RADIUS    = 4

    # ── Agent ───────────────────────────────
    AGENT_SPEED_DEFAULT = 8
    AGENT_SPEED_MIN     = 2
    AGENT_SPEED_MAX     = 30

    # ── Algorithms ──────────────────────────
    ASTAR_WEIGHT = 1.2
    ALGORITHMS   = ["A*", "Dijkstra", "BFS", "Greedy"]

    # ── Background / Grid base ──────────────
    C_BG          = (8, 10, 18)
    C_GRID        = (28, 28, 48)     # ✅ FIX: REQUIRED by renderer
    C_FREE        = (18, 18, 32)     # ✅ FIX: empty cell color
# ── Dynamic Obstacles ─────────────────────
    C_DYN_OBS = (210, 70, 50)
    # ── World objects ───────────────────────
    C_WALL        = (70, 72, 95)
    C_PATH        = (30, 200, 100)
    C_EXPLORED    = (25, 55, 100)
    C_FOG         = (8, 8, 14)

    C_START       = (255, 210, 0)
    C_GOAL        = (255, 70, 160)
    C_AGENT       = (0, 230, 170)

    C_CHECKPOINT        = (255, 160, 0)
    C_CHECKPOINT_DONE   = (100, 200, 80)

    # ── Panel UI ─────────────────────────────
    C_PANEL_BG    = (12, 14, 28)
    C_PANEL_LINE  = (60, 60, 90)

    # ── Text ────────────────────────────────
    C_TEXT        = (220, 220, 240)
    C_TEXT_DIM    = (140, 140, 170)

    # ── Accent colors ───────────────────────
    C_ACCENT      = (0, 255, 200)
    C_WARN        = (255, 180, 0)
    C_DANGER      = (255, 70, 90)

    # ── Buttons ─────────────────────────────
    C_BTN         = (25, 28, 50)
    C_BTN_HOVER   = (45, 55, 90)
    C_BTN_ACTIVE  = (0, 200, 160)

    # ── Slider ──────────────────────────────
    C_SLIDER_TRACK = (40, 40, 70)
    C_SLIDER_KNOB  = (0, 255, 200)

    # ── Energy ──────────────────────────────
    C_ENERGY_HI   = (0, 210, 120)
    C_ENERGY_MID  = (255, 200, 0)
    C_ENERGY_LO   = (255, 60, 60)

    # ── Heatmap ─────────────────────────────
    HEAT_COLORS = [
        (18, 18, 32),
        (20, 40, 80),
        (20, 80, 140),
        (20, 140, 160),
        (60, 180, 80),
        (180, 200, 40),
        (220, 140, 20),
        (220, 60, 20),
        (200, 20, 20)
    ]

    # ── Algorithm colors ────────────────────
    ALGO_COLORS = {
        "A*": (0, 200, 140),
        "Dijkstra": (80, 140, 255),
        "BFS": (255, 180, 0),
        "Greedy": (255, 80, 160)
    }

    # ── Output ──────────────────────────────
    SCREENSHOT_DIR = "outputs/screenshots"
    REPLAY_DIR     = "outputs/replays"