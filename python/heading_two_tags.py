"""Estimate a robot's heading from two tags (front and rear) read through a Q1 listener.

Mount one tag at the front of the robot and one at the rear, as far apart as the chassis allows.
Usage:
  python heading_two_tags.py --port /dev/ttyUSB0 --front 365D --rear 2C3C
"""
import argparse
import math
import time
from collections import deque

import serial

from q1_parse import parse_pos_line


def heading_deg(front, rear):
    """Heading in degrees, 0 = +X axis, counter-clockwise positive."""
    return math.degrees(math.atan2(front[1] - rear[1], front[0] - rear[0]))


def circular_mean_deg(angles):
    s = sum(math.sin(math.radians(a)) for a in angles)
    c = sum(math.cos(math.radians(a)) for a in angles)
    return math.degrees(math.atan2(s, c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--front", required=True, help="tag ID mounted at the front")
    ap.add_argument("--rear", required=True, help="tag ID mounted at the rear")
    ap.add_argument("--min-qf", type=int, default=60)
    ap.add_argument("--window", type=int, default=5, help="number of headings to average")
    args = ap.parse_args()

    latest = {}
    history = deque(maxlen=args.window)
    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        ser.write(b"\r")
        time.sleep(0.2)
        ser.write(b"lep\r")
        while True:
            pos = parse_pos_line(ser.readline().decode("utf-8", errors="ignore"))
            if pos is None or pos.tag_id is None or (pos.qf is not None and pos.qf < args.min_qf):
                continue
            latest[pos.tag_id.upper()] = (pos.x, pos.y)
            f, r = latest.get(args.front.upper()), latest.get(args.rear.upper())
            if f and r:
                history.append(heading_deg(f, r))
                print(f"heading={circular_mean_deg(history):7.1f} deg  center=({(f[0]+r[0])/2:.2f}, {(f[1]+r[1])/2:.2f})")


if __name__ == "__main__":
    main()
