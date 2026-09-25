"""Subscribe to tag positions published by a GrowSpace UWB Q1 gateway over MQTT.

Usage:
  pip install paho-mqtt
  python mqtt_subscriber.py --host 192.168.0.10
The gateway publishes under uwb/gateway/...; tag positions arrive as JSON with a `tags` array.
"""
import argparse
import json

import paho.mqtt.client as mqtt

from q1_parse import parse_gateway_tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True, help="MQTT broker address")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--topic", default="uwb/gateway/devices/#")
    args = ap.parse_args()

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except ValueError:
            return
        for pos in parse_gateway_tags(payload):
            print(f"{msg.topic} {pos.tag_id}: x={pos.x:.2f} y={pos.y:.2f} z={pos.z:.2f}")

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(args.host, args.port, 60)
    client.subscribe(args.topic)
    client.loop_forever()


if __name__ == "__main__":
    main()
