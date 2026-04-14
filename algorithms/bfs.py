"""
algorithms/bfs.py  —  Breadth-First Search.

Explores level by level.  Finds shortest path in terms of
number of hops (not Euclidean distance).  No edge weights.
"""

from collections import deque


def bfs(env, start: tuple, goal: tuple) -> tuple[list, set]:
    """
    Breadth-First Search.

    Parameters  env: GridEnvironment, start/goal: (row,col)
    Returns     (path, visited)
    """
    queue     = deque([start])
    came_from = {start: None}
    visited   = set()

    while queue:
        cur = queue.popleft()
        if cur in visited:
            continue
        visited.add(cur)

        if cur == goal:
            return _rebuild(came_from, cur), visited

        for nb in env.neighbors(*cur):
            if nb not in came_from:
                came_from[nb] = cur
                queue.append(nb)

    return [], visited


def _rebuild(came_from, cur):
    path = []
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path
