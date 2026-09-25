"""Read live coordinates from a GrowSpace UWB Q1 developer tag or listener over serial.

Usage:
  pip install pyserial
  python serial_reader.py --port /dev/ttyUSB0      # Linux / Raspberry Pi
  python serial_reader.py --port COM3              # Windows
"""
import argparse
import time

import serial

from q1_parse import parse_pos_line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--min-qf", type=int, default=60, help="drop positions below this quality factor")
    args = ap.parse_args()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        ser.write(b"\r")          # wake the shell
        time.sleep(0.2)
        ser.write(b"lep\r")       # start position output
        while True:
            line = ser.readline().decode("utf-8", errors="ignore")
            pos = parse_pos_line(line)
            if pos is None:
                continue
            if pos.qf is not None and pos.qf < args.min_qf:
                continue
            tag = pos.tag_id or "tag"
            print(f"{tag}: x={pos.x:.2f} y={pos.y:.2f} z={pos.z:.2f} qf={pos.qf}")


if __name__ == "__main__":
    main()
