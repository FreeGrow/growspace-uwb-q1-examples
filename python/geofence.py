"""Simple geofence for Q1 positions: alert when a tag enters a polygon zone.

Uses separate enter/exit margins (hysteresis) so the alert does not flicker at the boundary.
"""
from typing import List, Tuple

Point = Tuple[float, float]


def point_in_polygon(p: Point, poly: List[Point]) -> bool:
    x, y = p
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def distance_to_polygon_edge(p: Point, poly: List[Point]) -> float:
    def seg_dist(a, b):
        ax, ay = a
        bx, by = b
        px, py = p
        dx, dy = bx - ax, by - ay
        if dx == dy == 0:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        cx, cy = ax + t * dx, ay + t * dy
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
    return min(seg_dist(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


class Zone:
    def __init__(self, name: str, poly: List[Point], exit_margin: float = 0.3):
        self.name = name
        self.poly = poly
        self.exit_margin = exit_margin  # meters outside the edge before we call it "left"
        self.inside = {}

    def update(self, tag_id: str, p: Point):
        """Return 'enter', 'exit' or None for this tag."""
        was = self.inside.get(tag_id, False)
        now_in = point_in_polygon(p, self.poly)
        if not was and now_in:
            self.inside[tag_id] = True
            return "enter"
        if was and not now_in and distance_to_polygon_edge(p, self.poly) > self.exit_margin:
            self.inside[tag_id] = False
            return "exit"
        return None


if __name__ == "__main__":
    # Demo with simulated positions
    zone = Zone("forklift lane", [(0, 0), (4, 0), (4, 2), (0, 2)])
    for p in [(-1, 1), (0.1, 1), (-0.1, 1), (0.05, 1), (-0.5, 1)]:
        ev = zone.update("W01", p)
        print(p, ev or "")
