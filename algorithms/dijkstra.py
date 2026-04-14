"""
algorithms/dijkstra.py  —  Dijkstra's shortest-path algorithm.

Explores uniformly by actual cost.  Guaranteed optimal.
Slower than A* because it has no heuristic to guide the search.
"""

import heapq
import math


def dijkstra(env, start: tuple, goal: tuple) -> tuple[list, set]:
    """
    Dijkstra's algorithm (uniform-cost search).

    Parameters  env: GridEnvironment, start/goal: (row,col)
    Returns     (path, visited)
    """
    counter = 0
    heap    = [(0.0, counter, start)]
    came_from = {}
    g_score   = {start: 0.0}
    visited   = set()

    while heap:
        cost, _, cur = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)

        if cur == goal:
            return _rebuild(came_from, cur), visited

        for nb in env.neighbors(*cur):
            if nb in visited:
                continue
            dr = abs(nb[0] - cur[0])
            dc = abs(nb[1] - cur[1])
            edge = math.sqrt(2) if dr == 1 and dc == 1 else 1.0
            new_cost = g_score[cur] + edge

            if new_cost < g_score.get(nb, float("inf")):
                came_from[nb] = cur
                g_score[nb]   = new_cost
                counter += 1
                heapq.heappush(heap, (new_cost, counter, nb))

    return [], visited


def _rebuild(came_from, cur):
    path = [cur]
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path
