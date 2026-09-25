# Quickstart: UWB Indoor Positioning on Raspberry Pi

Read live indoor position data from a **GrowSpace UWB Creator Kit Q1** developer tag on a
Raspberry Pi, over UART, in about 10 minutes. No prior UWB experience needed.

한국어 버전: [quickstart-raspberry-pi.ko.md](quickstart-raspberry-pi.ko.md)

## What you need

- Raspberry Pi (any model with GPIO — Pi 3, 4, 5, or Zero 2 W all work)
- GrowSpace UWB Q1 developer tag ([kit details](https://grow-space.io/en/uwb-kit-en-2/))
- 3 jumper wires (GND, TX, RX)

## 1. Wire the tag to the 3.3 V header

The developer tag has **two separate connectors** — use the **3.3 V one (left side)**.
Never wire the 5 V connector to a Raspberry Pi: the Pi's GPIO UART is 3.3 V logic and the
5 V side can damage it.

| Tag pin | Raspberry Pi GPIO pin |
|---|---|
| GND | Pin 6 (GND) |
| TX  | Pin 10 (GPIO15 / RXD) |
| RX  | Pin 8 (GPIO14 / TXD) |

TX on the tag goes to RX on the Pi, and RX on the tag goes to TX on the Pi — always cross
the two data lines.

## 2. Free up the Pi's UART

By default, Raspberry Pi OS uses the primary UART as a login console, which will fight your
script for the port.

```bash
sudo raspi-config
# Interface Options → Serial Port
#   "Would you like a login shell over serial?" → No
#   "Would you like the serial port hardware enabled?" → Yes
sudo reboot
```

## 3. Install and run the example

```bash
git clone https://github.com/FreeGrow/growspace-uwb-q1-examples.git
cd growspace-uwb-q1-examples/python
pip install -r requirements.txt

python serial_reader.py --port /dev/serial0
```

You should see a stream of positions:

```
POS,-3.41,9.54,-1.53,74
```

That's `x, y, z` in meters, and a quality factor (`qf`) from 0–100. Values of 60+ are
generally stable enough to build on directly.

If nothing prints, see the [troubleshooting guide](troubleshooting.md#raspberry-pi-uart-not-responding-or-the-pi-resets).

## 4. See it on a live map

The repo includes a small web dashboard that plots tags on a floor plan in real time, with
geofence zones and per-tag labels:

```bash
cd visualizer
pip install -r requirements.txt
python server.py --source serial --port /dev/serial0
```

Open `http://<your-pi-ip>:8000` from any browser on the same network.

## Next steps

- Multiple tags at once: point several `serial_reader.py` instances at different ports, or
  use a **listener** module instead of a developer tag — a listener reports `POS,idx,tagId,x,y,z,qf`
  for every tag it hears, so one Pi can track many tags through a single serial connection.
- Zone alerts: `python/geofence.py` has a point-in-polygon example with enter/exit hysteresis,
  useful for triggering an action when a tag crosses a boundary.
- Full Raspberry Pi guide (power, enclosure notes, multi-tag setups):
  https://grow-space.io/en/docs/q1-en/raspberry-pi-en/
