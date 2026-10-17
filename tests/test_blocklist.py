import os
import sys
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp()
os.environ["LOG_FILE"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "sample.log")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import blocklist  # noqa: E402
from app import app  # noqa: E402


def raises(fn, *args):
    try:
        fn(*args)
    except blocklist.BlockError:
        return True
    return False


def test_validation_rejects_bad_and_private():
    assert raises(blocklist.validate_ip, "not-an-ip")
    assert raises(blocklist.validate_ip, "10.0.0.5")
    assert raises(blocklist.validate_ip, "127.0.0.1")
    assert blocklist.validate_ip(" 185.220.101.4 ") == "185.220.101.4"


def test_block_unblock_and_audit():
    blocklist.block("8.8.8.8", "test")
    assert blocklist.is_blocked("8.8.8.8")
    assert raises(blocklist.block, "8.8.8.8")        # duplicate
    blocklist.unblock("8.8.8.8")
    assert not blocklist.is_blocked("8.8.8.8")
    assert raises(blocklist.unblock, "8.8.8.8")      # not blocked
    actions = [a["action"] for a in blocklist.read_audit()]
    assert actions[:2] == ["unblock", "block"]


def test_api_requires_json_and_blocks():
    c = app.test_client()
    assert c.post("/api/block", data={"ip": "1.2.3.4"}).status_code == 400
    r = c.post("/api/block", json={"ip": "1.1.1.1", "reason": "x"})
    assert r.get_json()["ok"] is True
    sugg = c.get("/api/suggestions?threshold=1").get_json()
    assert all(not s["ip"].startswith("10.") for s in sugg)
    assert "1.1.1.1" not in [s["ip"] for s in sugg]
    assert c.post("/api/block", json={"ip": "10.0.0.2"}).status_code == 400
