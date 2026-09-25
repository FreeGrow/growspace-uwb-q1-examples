"""Live web dashboard for GrowSpace UWB Q1 positions.

Shows tags moving on a 2D floor plan, lets you assign a friendly label to each
tag ID, and flashes a geofence zone red/green when a tag enters or leaves it.

Three data sources:
  --source demo     simulated tags, no hardware needed (try the UI first)
  --source serial   a Q1 developer tag or listener over USB serial
  --source mqtt     a Q1 gateway over MQTT

Usage:
  pip install -r requirements.txt
  python server.py --source demo
  python server.py --source serial --port /dev/ttyUSB0
  python server.py --source mqtt --host 192.168.0.10
Then open http://localhost:8000

Zones are defined in zones.example.json (edit or point --zones at your own file):
  [{"name": "forklift lane", "polygon": [[0,0],[4,0],[4,2],[0,2]], "exit_margin": 0.3}]
"""
import argparse
import json
import math
import queue
import sys
import threading
import time
from pathlib import Path

from flask import Flask, Response, jsonify, send_from_directory

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
sys.path.insert(0, str(APP_DIR.parent))  # reuse q1_parse.py / geofence.py from ../

from q1_parse import Position, parse_gateway_tags, parse_pos_line  # noqa: E402
from geofence import Zone  # noqa: E402

app = Flask(__name__, static_folder=None)

_subscribers = []
_subscribers_lock = threading.Lock()


def broadcast(event: dict) -> None:
    data = json.dumps(event)
    with _subscribers_lock:
        for q in _subscribers:
            q.put(data)


def load_zones(path):
    """Load zone polygons from a JSON file. Returns [] if the file is missing."""
    if not path or not Path(path).exists():
        return []
    raw = json.loads(Path(path).read_text())
    zones = []
    for z in raw:
        zones.append({
            "obj": Zone(z["name"], [tuple(pt) for pt in z["polygon"]], z.get("exit_margin", 0.3)),
            "def": z,
        })
    return zones


def handle_position(pos: Position, zones) -> None:
    tag_id = pos.tag_id or "tag"
    broadcast({"type": "position", "tag_id": tag_id, "x": pos.x, "y": pos.y, "z": pos.z, "qf": pos.qf})
    for z in zones:
        ev = z["obj"].update(tag_id, (pos.x, pos.y))
        if ev:
            broadcast({"type": "geofence", "tag_id": tag_id, "zone": z["obj"].name, "event": ev})


def run_demo(zones) -> None:
    """Simulate two tags walking in circles so the UI can be tried with no hardware."""
    t = 0.0
    while True:
        t += 0.15
        for tag_id, x, y in [
            ("DEMO1", 3 + 2.5 * math.cos(t), 2 + 2.5 * math.sin(t)),
            ("DEMO2", 3 + 1.2 * math.cos(-t * 0.7 + 1.5), 2 + 1.2 * math.sin(-t * 0.7 + 1.5)),
        ]:
            handle_position(Position(tag_id, x, y, 0.0, 90), zones)
        time.sleep(0.2)


def run_serial(port, baud, zones) -> None:
    import serial

    with serial.Serial(port, baud, timeout=1) as ser:
        ser.write(b"\r")
        time.sleep(0.2)
        ser.write(b"lep\r")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore")
            pos = parse_pos_line(line)
            if pos:
                handle_position(pos, zones)


def run_mqtt(host, port, topic, zones) -> None:
    import paho.mqtt.client as mqtt

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except ValueError:
            return
        for pos in parse_gateway_tags(payload):
            handle_position(pos, zones)

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(host, port, 60)
    client.subscribe(topic)
    client.loop_forever()


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/zones.json")
def zones_json():
    return jsonify([z["def"] for z in app.config.get("ZONES", [])])


@app.route("/stream")
def stream():
    q = queue.Queue()
    with _subscribers_lock:
        _subscribers.append(q)

    def gen():
        try:
            yield "retry: 2000\n\n"
            while True:
                yield f"data: {q.get()}\n\n"
        finally:
            with _subscribers_lock:
                if q in _subscribers:
                    _subscribers.remove(q)

    return Response(gen(), mimetype="text/event-stream")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["demo", "serial", "mqtt"], default="demo")
    ap.add_argument("--port", help="serial port, e.g. /dev/ttyUSB0 or COM3")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--host", help="MQTT broker address")
    ap.add_argument("--mqtt-port", type=int, default=1883)
    ap.add_argument("--topic", default="uwb/gateway/devices/#")
    ap.add_argument("--zones", default=str(APP_DIR / "zones.example.json"))
    ap.add_argument("--web-port", type=int, default=8000)
    args = ap.parse_args()

    zones = load_zones(args.zones)
    app.config["ZONES"] = zones

    if args.source == "demo":
        t = threading.Thread(target=run_demo, args=(zones,), daemon=True)
    elif args.source == "serial":
        if not args.port:
            ap.error("--source serial requires --port")
        t = threading.Thread(target=run_serial, args=(args.port, args.baud, zones), daemon=True)
    else:
        if not args.host:
            ap.error("--source mqtt requires --host")
        t = threading.Thread(target=run_mqtt, args=(args.host, args.mqtt_port, args.topic, zones), daemon=True)
    t.start()

    print(f"Open http://localhost:{args.web_port}")
    app.run(host="0.0.0.0", port=args.web_port, threaded=True)


if __name__ == "__main__":
    main()
