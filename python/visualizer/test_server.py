import json
import queue
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server as srv  # noqa: E402
from q1_parse import Position  # noqa: E402


def _write_zones(tmp_path):
    zones_file = tmp_path / "zones.json"
    zones_file.write_text(json.dumps([
        {"name": "zone a", "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]], "exit_margin": 0.2}
    ]))
    return str(zones_file)


def test_load_zones(tmp_path):
    zones = srv.load_zones(_write_zones(tmp_path))
    assert len(zones) == 1
    assert zones[0]["obj"].name == "zone a"
    assert zones[0]["def"]["name"] == "zone a"


def test_load_zones_missing_file():
    assert srv.load_zones("/no/such/file.json") == []


def test_handle_position_broadcasts_position_and_geofence(tmp_path):
    zones = srv.load_zones(_write_zones(tmp_path))

    srv._subscribers.clear()
    q = queue.Queue()
    srv._subscribers.append(q)

    srv.handle_position(Position("T1", 1.0, 1.0, 0.0, 90), zones)

    events = []
    while not q.empty():
        events.append(json.loads(q.get()))

    types = [e["type"] for e in events]
    assert "position" in types
    assert "geofence" in types
    geofence_events = [e for e in events if e["type"] == "geofence"]
    assert geofence_events[0]["event"] == "enter"
    assert geofence_events[0]["zone"] == "zone a"

    srv._subscribers.remove(q)


def test_zones_endpoint():
    srv.app.config["ZONES"] = [{"def": {"name": "z", "polygon": [[0, 0], [1, 0], [1, 1]]}}]
    client = srv.app.test_client()
    resp = client.get("/zones.json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["name"] == "z"


def test_index_serves_html():
    client = srv.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Live Viewer" in resp.data
