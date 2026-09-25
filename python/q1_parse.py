"""Parsers for GrowSpace UWB Q1 serial and MQTT output.

Serial output after sending `lep`:
  Developer tag : POS,x,y,z,qf                 e.g. POS,-3.41,9.54,-1.53,74
  Listener      : POS,idx,tagId,x,y,z,qf       e.g. POS,0,365D,-3.41,9.54,-1.53,74
Coordinates are in meters. QF is a 0-100 quality factor (higher is better).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    tag_id: Optional[str]
    x: float
    y: float
    z: float
    qf: Optional[int]


def parse_pos_line(line: str) -> Optional[Position]:
    """Parse one `POS,...` line. Returns None for anything else or broken lines."""
    parts = line.strip().split(",")
    if not parts or parts[0] != "POS":
        return None
    try:
        if len(parts) == 5:  # developer tag: POS,x,y,z,qf
            return Position(None, float(parts[1]), float(parts[2]), float(parts[3]), int(parts[4]))
        if len(parts) >= 7:  # listener: POS,idx,tagId,x,y,z,qf
            return Position(parts[2], float(parts[3]), float(parts[4]), float(parts[5]), int(parts[6]))
    except ValueError:
        return None
    return None


def parse_gateway_tags(payload: dict) -> list:
    """Parse a gateway MQTT message that carries a `tags` array.

    Example payload:
      {"gatewayID": "GR21BA", "tags": [{"id": "GR2c3c", "panID": "0001", "x": -3.95, "y": 0.23, "z": -2.48}]}
    """
    out = []
    for t in payload.get("tags", []):
        try:
            out.append(Position(t.get("id"), float(t["x"]), float(t["y"]), float(t["z"]), None))
        except (KeyError, TypeError, ValueError):
            continue
    return out
