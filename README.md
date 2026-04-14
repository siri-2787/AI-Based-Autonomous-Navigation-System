<div align="center">



# 🤖   AI-Based Autonomous Navigation System

### AI-Powered Path Planning with Real-Time Obstacle Avoidance

![Python](https://img.shields.io/badge/PYTHON-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/PYGAME-2.5.2-green?style=for-the-badge&logo=python&logoColor=white)
![Algorithm](https://img.shields.io/badge/A*%20%7C%20DIJKSTRA%20%7C%20BFS%20%7C%20GREEDY-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/STATUS-ACTIVE-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/LICENSE-MIT-yellow?style=for-the-badge)

![Algorithms](https://img.shields.io/badge/Algorithms-4-blueviolet)
![Replanning](https://img.shields.io/badge/Real--Time%20Replanning-✓-green)
![FogOfWar](https://img.shields.io/badge/Fog%20of%20War-✓-blue)
![Energy](https://img.shields.io/badge/Energy%20System-✓-orange)
![Replay](https://img.shields.io/badge/Save%20%26%20Replay-✓-red)

**A\* Path Planning · Dijkstra · BFS · Greedy Best-First · Dynamic Obstacles · Fog of War · Energy System · Save & Replay**

[🚀 Quick Start](#-quick-start) • [📊 Features](#-features) • [🏗️ Architecture](#%EF%B8%8F-architecture) • [▶️ Run Demo](#%EF%B8%8F-how-to-run) • [📸 Screenshots](#-screenshots)

</div>

---

## 📌 Overview

** AI-Based Autonomous Navigation System** is a production-quality simulation of an AI robot navigating a dynamic obstacle-filled environment. It supports **4 pathfinding algorithms**, **real-time replanning**, **fog of war**, a **fuel/energy system**, **checkpoint navigation**, and a full **save & replay system** — all running at 60 FPS in a custom Pygame simulation.

> Built as a Final Year Project at **Netaji Subhash Engineering College, Kolkata** to demonstrate AI, algorithms, and software architecture skills for placement and internship applications.

---

## 🎯 Problem Statement

Real-world autonomous robots must:
- **Perceive** the environment with limited sensor range
- **Plan** the optimal route from start to goal
- **React** instantly when new obstacles appear
- **Navigate** through checkpoints while managing resources (energy/fuel)

This project simulates all of the above in a fully interactive virtual environment — **no GPU, no hardware required**.

---

## 🏭 Industry Relevance

| Domain | Real-World Application |
|---|---|
| 🏭 Warehouse Automation | Amazon Kiva robots, autonomous forklifts |
| 🚗 Self-Driving Cars | Waymo, Tesla Autopilot path planning stack |
| 🚁 Drone Navigation | Delivery drones, inspection UAVs |
| 🏥 Medical Robotics | Hospital delivery bots |
| 🤖 Industrial AGVs | Obstacle-aware factory floor automation |

---

## ✨ Features

### 🧠 4 Pathfinding Algorithms (switchable via dropdown)
| Algorithm | Strategy | Optimal? | Speed |
|---|---|---|---|
| **A\*** | g(n) + w·h(n) — weighted heuristic | ✅ Near-optimal | ⚡ Fast |
| **Dijkstra** | Uniform cost search | ✅ Optimal | 🐢 Slow |
| **BFS** | Level-by-level expansion | ✅ Hop-optimal | 🐢 Slow |
| **Greedy** | Pure heuristic, goal-directed | ❌ Sub-optimal | ⚡ Fastest |

### ⚡ Real-Time Replanning
When a dynamic obstacle moves onto the planned path, the agent **instantly replans** without freezing the simulation.

### 🎮 Full Simulation Features
- **Moving obstacles** — 6 bouncing dynamic obstacles
- **Checkpoints** — agent visits 2 waypoints before reaching the goal
- **Energy / Fuel system** — bar depletes per move, agent halts at zero
- **Fog of War** — hidden cells revealed progressively as agent moves
- **Heatmap mode** — visualise cumulative A\* exploration across all replans
- **Click to paint** — add/remove obstacles live by clicking the grid
- **Speed slider** — control agent speed in real time
- **Save & Replay** — record a run to JSON, replay it later
- **Multi-algorithm comparison** — run all 4 at once, compare metrics

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    IANS SYSTEM PIPELINE                    │
│                                                            │
│  ┌──────────────┐    ┌──────────────┐   ┌──────────────┐  │
│  │  GridEnv     │───▶│  Algorithm   │──▶│    Agent     │  │
│  │  (World)     │    │  Registry    │   │  (Robot)     │  │
│  │              │    │  A* / Dijk   │   │              │  │
│  │  • Static    │    │  / BFS /     │   │  • Energy    │  │
│  │    obstacles │    │    Greedy    │   │  • Sensor    │  │
│  │  • Dynamic   │    └──────────────┘   │  • Checkpts  │  │
│  │    movers    │                       └──────┬───────┘  │
│  │  • Fog/Heat  │    ┌──────────────┐          │          │
│  │  • Checkpts  │◀───│  SimEngine   │◀─────────┘          │
│  └──────────────┘    │  (State      │                      │
│                      │   Machine)   │                      │
│                      └──────┬───────┘                      │
│                             │                              │
│              ┌──────────────┴──────────────┐               │
│              │                             │               │
│       ┌──────▼──────┐             ┌────────▼──────┐        │
│       │  Renderer   │             │   HUD Panel   │        │
│       │  (Grid/Fog/ │             │   (Stats/     │        │
│       │   Heatmap/  │             │    Compare/   │        │
│       │   Agent)    │             │    Energy)    │        │
│       └─────────────┘             └───────────────┘        │
└────────────────────────────────────────────────────────────┘
```

### State Machine
```
IDLE ──▶ PLANNING ──▶ NAVIGATING ──▶ CHECKPOINT ──▶ NAVIGATING
                           │                              │
                      REPLANNING ◀─ obstacle detected     │
                           │                              ▼
                       NO_PATH                         REACHED
                       OUT_ENERGY
```

---

## 📁 Folder Structure

```
Intelligent-Autonomous-Navigation-System/
│
├── main.py                          ← 🚀 Entry point — run this
├── app.py                           ← Pygame window + UI wiring
├── config.py                        ← All constants in one place
│
├── algorithms/
│   ├── __init__.py                  ← run_algorithm() + compare_all()
│   ├── astar.py                     ← Weighted A* (diagonal movement)
│   ├── dijkstra.py                  ← Uniform-cost search
│   ├── bfs.py                       ← Breadth-First Search
│   └── greedy.py                    ← Greedy Best-First Search
│
├── engine/
│   ├── environment.py               ← Grid world + fog + heatmap + checkpoints
│   ├── agent.py                     ← Robot + energy + sensor + replay log
│   ├── simulation.py                ← SimEngine state machine
│   └── recorder.py                  ← Save run to JSON + replay playback
│
├── components/
│   ├── renderer.py                  ← Draws grid, heatmap, fog, agent, path
│   ├── hud.py                       ← Stats panel + comparison table + energy bar
│   └── controls.py                  ← Button, Toggle, Slider, Dropdown widgets
│
├── utils/
│   └── helpers.py                   ← path_length(), clamp(), lerp()
│
├── outputs/
│   ├── screenshots/                 ← Auto-saved screenshots (S key)
│   └── replays/                     ← Saved run JSON files
│
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.11** (recommended — pygame 2.5.2 has pre-built wheels for 3.11)
- pip

### Step 1 — Clone
```bash
git clone https://github.com/siri-2787/AI-Based Autonomous Navigation System.git
cd AI-Based Autonomous Navigation System
```

### Step 2 — Virtual environment
```bash
# Windows
py -3.11 -m venv venv
venv\Scripts\activate
```

### Step 3 — Install
```bash
pip install -r requirements.txt
```

### Step 4 — Run
```bash
python main.py
```

---

## ▶️ How to Run

### Full Simulation
```bash
python main.py
```

### Keyboard Shortcuts
| Key | Action |
|---|---|
| `ENTER` | Start navigation |
| `SPACE` | Pause / Resume |
| `R` | Reset — new random map |
| `C` | Compare all 4 algorithms |
| `S` | Save screenshot |
| `ESC` | Quit |

### Mouse Controls
| Action | Effect |
|---|---|
| Click algorithm dropdown | Switch algorithm |
| Click grid cell | Toggle obstacle on/off |
| Drag speed slider | Change agent speed |
| Click toggles | Grid lines / Fog / Heatmap / Checkpoints |

---

## 📊 Algorithm Comparison (Sample Run — 36×28 grid)

| Algorithm | Path Length | Nodes Explored | Time (ms) | Optimal? |
|---|---|---|---|---|
| **A\*** | 46.3 | 46 | 0.37 | ✅ Near |
| **Dijkstra** | 45.7 | 747 | 3.61 | ✅ Yes |
| **BFS** | 45.7 | 747 | 3.21 | ✅ Hop |
| **Greedy** | 46.9 | 41 | 0.35 | ❌ No |

> A\* explores **16× fewer nodes** than Dijkstra while finding near-optimal paths.

---

## 📸 Screenshots

| Simulation Running | Algorithm Comparison | Fog of War |
|---|---|---|
| ![sim](images/sim_running.png) | ![compare](images/comparison.png) | ![fog](images/fog_of_war.png) |

---

## 🔮 Future Improvements

- [ ] YOLOv8 real-camera obstacle detection
- [ ] ROS 2 bridge for real robot control
- [ ] CARLA 3-D simulator integration
- [ ] Reinforcement Learning agent (DQN/PPO replacing A\*)
- [ ] SLAM — build map while navigating (no prior knowledge)
- [ ] Multi-agent coordination (multiple robots)
- [ ] 3-D drone navigation version
- [ ] Cloud telemetry dashboard

---

## 🧠 Learning Outcomes

- Implemented **4 graph search algorithms** from scratch with proper data structures
- Built a modular **simulation pipeline** separating concerns across engine / components / algorithms
- Applied **dynamic replanning** strategy for real-time obstacle avoidance
- Designed a **sensor abstraction layer** simulating LIDAR proximity detection
- Created a **Save & Replay system** using JSON serialization
- Practiced production-quality **Python project architecture**

---

## 👤 Author

**P SIRI REDDY**
B.Tech CSE, CBIT

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.

---

<div align="center">
⭐ If this project helped you, please give it a star!
</div>
