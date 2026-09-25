from q1_parse import parse_pos_line, parse_gateway_tags
from heading_two_tags import heading_deg
from geofence import Zone


def test_tag_line():
    p = parse_pos_line("POS,-3.41,9.54,-1.53,74")
    assert p and p.tag_id is None and p.x == -3.41 and p.qf == 74


def test_listener_line():
    p = parse_pos_line("POS,0,365D,-3.41,9.54,-1.53,74\r\n")
    assert p and p.tag_id == "365D" and p.z == -1.53


def test_garbage():
    assert parse_pos_line("dwm> lep") is None
    assert parse_pos_line("POS,0,365D,xx,9.54,-1.53,74") is None


def test_gateway():
    tags = parse_gateway_tags({"gatewayID": "GR21BA", "tags": [{"id": "GR2c3c", "panID": "0001", "x": -3.95, "y": 0.23, "z": -2.48}]})
    assert tags[0].tag_id == "GR2c3c" and tags[0].x == -3.95


def test_heading():
    assert round(heading_deg((1, 1), (0, 0))) == 45


def test_geofence_hysteresis():
    z = Zone("a", [(0, 0), (4, 0), (4, 2), (0, 2)], exit_margin=0.3)
    assert z.update("t", (1, 1)) == "enter"
    assert z.update("t", (-0.1, 1)) is None
    assert z.update("t", (-0.5, 1)) == "exit"
