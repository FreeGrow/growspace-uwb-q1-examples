# UWB Q1 Troubleshooting Guide

Common problems when wiring or reading data from the **GrowSpace UWB Creator Kit Q1**
(developer tag, listener, or gateway), and how to fix them. If your issue isn't listed here,
[open an issue](https://github.com/FreeGrow/growspace-uwb-q1-examples/issues) or check the
[full documentation](https://grow-space.io/en/docs/q1-en/).

한국어 버전: [troubleshooting.ko.md](troubleshooting.ko.md)

## No data on the serial port

**Symptom:** `serial_reader.py` connects but never prints a line, or times out.

1. **Send `lep` first.** The tag and listener are silent until you send the `lep` command
   over serial. Without it, nothing streams out.
2. **Check the baud rate.** The kit talks at **115200 bps**. A mismatched baud rate looks
   like "no data" or garbled text, not an error.
3. **Cross TX↔RX.** If you wired TX→TX and RX→RX by mistake, the port opens fine but
   nothing is ever received. Swap the two wires.
4. **Confirm the port name.** On Linux it's usually `/dev/ttyUSB0` or `/dev/ttyACM0`; on
   Windows, a `COMx` port. Run `python -m serial.tools.list_ports` to list what's attached.

## Garbled or partial text on the line

**Symptom:** You see fragments like `POS,-3.4` cut off, or non-ASCII noise.

- This is almost always a **baud rate mismatch** — double-check both sides are set to
  115200.
- A loose or too-long jumper wire on a breadboard can also corrupt a UART signal at this
  baud rate. Keep wiring short and check for a solid connection.

## Positions never stabilize / `qf` stays low

**Symptom:** Coordinates stream in, but the quality factor (`qf`) is consistently below 40–50,
or the position jumps around.

- **`qf` is a 0–100 confidence score.** Values of 60 and above are usually stable enough to
  use directly; treat anything under that as noisy and filter it (see
  `python/serial_reader.py` for a `--min-qf` example).
- **Line-of-sight matters.** UWB ranging degrades through thick walls, metal shelving, or
  when the tag is very close to a listener's mounting surface.
- **Anchor/listener geometry.** If all your listeners are roughly in a line, positions along
  the perpendicular axis will be less accurate. Spread listeners out in two dimensions where
  possible.

## Raspberry Pi: UART not responding, or the Pi resets

**Symptom:** Nothing on `/dev/serial0`, or the Raspberry Pi becomes unstable right after
wiring the tag.

- **Use the 3.3 V side of the tag, never the 5 V side.** The developer tag has two separate
  connectors — **5 V is on the right, 3.3 V is on the left**. Wiring the 5 V side into a
  Raspberry Pi's GPIO UART pins can damage the Pi's UART input, since the Pi's GPIO is a
  3.3 V logic level.
- **Disable the Linux serial console** on `/dev/serial0` first (`raspi-config` →
  Interface Options → Serial Port → login shell: No, hardware enabled: Yes), or the OS will
  fight with your script for the port.
- Full walkthrough: https://grow-space.io/en/docs/q1-en/raspberry-pi-en/

## ESP32: serial port keeps disconnecting or resetting

**Symptom:** The USB-serial connection to the ESP32 drops intermittently while reading tag
data, or the board reboots.

- Use a **hardware UART** pair (e.g. `Serial1`/`Serial2`) rather than bit-banged software
  serial where possible — ESP32 has multiple hardware UARTs and is much more reliable at
  115200 bps than a software-serial library.
- Some ESP32 dev boards brown out under load from a single USB port when a tag is also
  drawing power from the same rail — use a powered hub or separate 5 V supply if you see
  random resets.
- Full walkthrough: https://grow-space.io/en/docs/q1-en/esp32-en/

## Arduino Uno: AltSoftSerial not receiving anything

**Symptom:** `arduino/uno_altsoftserial` compiles and uploads, but nothing prints.

- **AltSoftSerial is pinned to specific pins on the Uno** (RX on D8, TX on D9 in this
  example) — you cannot move it to arbitrary pins without changing libraries.
- The Uno's single hardware `Serial` is normally used for USB debug output, which is why
  this example uses AltSoftSerial for the tag connection — don't wire the tag onto D0/D1.
- For a project needing multiple simultaneous serial reads, an **Arduino Mega 2560** with a
  free hardware `Serial1`/`Serial2`/`Serial3` (see `arduino/mega_serial1`) is more reliable
  than software serial.

## MQTT: gateway messages never arrive

**Symptom:** `mqtt_subscriber.py` connects to the broker but no messages show up on the
`uwb/gateway/...` topic.

- Confirm the gateway and your subscriber are on the **same MQTT broker and topic prefix** —
  check the broker address configured on the gateway itself, not just the subscriber script.
- Gateway payloads are JSON with a `tags` array (`{"gatewayID":"...","tags":[{"id":"...",
  "x":...,"y":...,"z":...}]}`) — if you're filtering by topic, make sure the wildcard covers
  the gateway ID segment.
- Firewalled networks sometimes block the MQTT port (1883, or 8883 for TLS) between subnets —
  confirm the gateway and your machine can actually reach the broker.

## Still stuck?

- Command reference: https://grow-space.io/en/docs/q1-en/commands-en/
- MQTT format reference: https://grow-space.io/en/docs/q1-en/mqtt-data-format-en/
- Ask a question or request a quote: https://grow-space.io/en/uwb-kit-en-2/#inquiry
