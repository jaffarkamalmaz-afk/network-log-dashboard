"""Simulated firewall: a blocklist plus an audit log, stored as local files.

Nothing here touches a real firewall. Blocking an address only records it
in data/blocklist.json so the dashboard can show it as blocked.
"""
import ipaddress
import json
import os
from datetime import datetime

DATA_DIR = os.environ.get("DATA_DIR", "data")


class BlockError(ValueError):
    """Raised when a block or unblock request is not allowed."""


def _path(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, name)


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _read_blocklist():
    try:
        with open(_path("blocklist.json"), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_blocklist(data):
    with open(_path("blocklist.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def log_action(action, ip, actor, detail=""):
    entry = {"time": _now(), "action": action, "ip": ip, "actor": actor, "detail": detail}
    with open(_path("audit.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_audit(limit=50):
    try:
        with open(_path("audit.log"), encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    entries = []
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries[::-1]


def validate_ip(value):
    """Return a normalized public IP string, or raise BlockError."""
    try:
        ip = ipaddress.ip_address(str(value).strip())
    except ValueError:
        raise BlockError("Not a valid IP address")
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
        raise BlockError("Protected address: private and local addresses cannot be blocked")
    return str(ip)


def list_blocked():
    data = _read_blocklist()
    return [dict(ip=ip, **info) for ip, info in sorted(data.items())]


def is_blocked(ip):
    return ip in _read_blocklist()


def block(ip, reason="", actor="admin"):
    ip = validate_ip(ip)
    data = _read_blocklist()
    if ip in data:
        raise BlockError("Already blocked")
    data[ip] = {"since": _now(), "reason": reason[:200], "by": actor}
    _write_blocklist(data)
    log_action("block", ip, actor, reason[:200])
    return ip


def unblock(ip, actor="admin"):
    ip = str(ip).strip()
    data = _read_blocklist()
    if ip not in data:
        raise BlockError("Not in the blocklist")
    del data[ip]
    _write_blocklist(data)
    log_action("unblock", ip, actor)
    return ip
