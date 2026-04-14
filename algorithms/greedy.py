"""
algorithms/greedy.py  —  Greedy Best-First Search.

Always expands the node that looks closest to the goal (pure heuristic).
Very fast but NOT guaranteed optimal — may find a longer path.
"""

import heapq
import math


def heuristic(a: tuple, b: tuple) -> float:
    """Chebyshev distance."""
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dr + dc) + (math.sqrt(2) - 2) * min(dr, dc)


def greedy(env, start: tuple, goal: tuple) -> tuple[list, set]:
    """
    Greedy Best-First Search.

    Parameters  env: GridEnvironment, start/goal: (row,col)
    Returns     (path, visited)
    """
    counter   = 0
    heap      = [(heuristic(start, goal), counter, start)]
    came_from = {start: None}
    visited   = set()

    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)

        if cur == goal:
            return _rebuild(came_from, cur), visited

        for nb in env.neighbors(*cur):
            if nb not in came_from:
                came_from[nb] = cur
                h = heuristic(nb, goal)
                counter += 1
                heapq.heappush(heap, (h, counter, nb))

    return [], visited


def _rebuild(came_from, cur):
    path = []
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path
