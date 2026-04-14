"""
algorithms/__init__.py
Unified registry — import one function to run any algorithm.

Usage:
    from algorithms import run_algorithm
    path, visited, time_ms = run_algorithm("A*", env, start, goal)
"""

import time
from algorithms.astar    import astar
from algorithms.dijkstra import dijkstra
from algorithms.bfs      import bfs
from algorithms.greedy   import greedy


_REGISTRY = {
    "A*":       astar,
    "Dijkstra": dijkstra,
    "BFS":      bfs,
    "Greedy":   greedy,
}


def run_algorithm(name: str, env, start: tuple, goal: tuple) -> tuple:
    """
    Run the named algorithm.

    Returns
    -------
    path     : list[(row,col)] — empty if no path
    visited  : set[(row,col)] — all explored nodes
    time_ms  : float          — wall-clock time in milliseconds
    """
    fn = _REGISTRY.get(name)
    if fn is None:
        raise ValueError(f"Unknown algorithm: {name!r}. "
                         f"Choose from {list(_REGISTRY)}")
    t0 = time.perf_counter()
    path, visited = fn(env, start, goal)
    t1 = time.perf_counter()
    return path, visited, round((t1 - t0) * 1000, 3)


def compare_all(env, start: tuple, goal: tuple) -> dict:
    """
    Run every registered algorithm and return a comparison dict.

    Returns
    -------
    { algo_name: {"path": [...], "visited": set,
                  "time_ms": float, "length": float,
                  "nodes": int} }
    """
    from utils.helpers import path_length
    results = {}
    for name in _REGISTRY:
        path, visited, ms = run_algorithm(name, env, start, goal)
        results[name] = {
            "path":    path,
            "visited": visited,
            "time_ms": ms,
            "length":  path_length(path) if path else 0.0,
            "nodes":   len(visited),
        }
    return results
