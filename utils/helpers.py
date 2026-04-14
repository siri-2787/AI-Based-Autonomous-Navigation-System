"""utils/helpers.py — shared utility functions."""
import math


def path_length(path: list) -> float:
    """Euclidean length of a path (list of (r,c) tuples)."""
    total = 0.0
    for i in range(1, len(path)):
        dr = path[i][0] - path[i-1][0]
        dc = path[i][1] - path[i-1][1]
        total += math.sqrt(dr*dr + dc*dc)
    return round(total, 2)


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def lerp(a, b, t):
    return a + t * (b - a)
