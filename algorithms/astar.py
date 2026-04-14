"""
algorithms/astar.py  —  Weighted A* with diagonal movement.

f(n) = g(n) + w * h(n)
w = 1  → optimal A*
w > 1  → faster, slightly sub-optimal (Weighted A*)
"""

import heapq
import math
from config import Cfg


def heuristic(a: tuple, b: tuple) -> float:
    """Chebyshev distance — admissible for 8-directional movement."""
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dr + dc) + (math.sqrt(2) - 2) * min(dr, dc)


def astar(env, start: tuple, goal: tuple) -> tuple[list, set]:
    """
    Weighted A* search.

    Parameters  env: GridEnvironment, start/goal: (row,col)
    Returns     (path, visited)
    """
    w       = Cfg.ASTAR_WEIGHT
    counter = 0
    heap    = []
    heapq.heappush(heap, (0.0, counter, start))

    came_from = {}
    g_score   = {start: 0.0}
    open_set  = {start}
    visited   = set()

    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)
        open_set.discard(cur)

        if cur == goal:
            return _rebuild(came_from, cur), visited

        for nb in env.neighbors(*cur):
            if nb in visited:
                continue
            dr = abs(nb[0] - cur[0])
            dc = abs(nb[1] - cur[1])
            cost = math.sqrt(2) if dr == 1 and dc == 1 else 1.0
            tg   = g_score[cur] + cost

            if tg < g_score.get(nb, float("inf")):
                came_from[nb] = cur
                g_score[nb]   = tg
                f             = tg + w * heuristic(nb, goal)
                counter += 1
                heapq.heappush(heap, (f, counter, nb))
                open_set.add(nb)

    return [], visited


def _rebuild(came_from, cur):
    path = [cur]
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path
