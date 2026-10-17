"""Parse and summarize log files.

Line format:  YYYY-MM-DD HH:MM:SS|LEVEL|SERVICE|IP|MESSAGE
"""
from collections import Counter
from datetime import datetime

LEVELS = ("INFO", "WARNING", "ERROR")


def parse_line(line):
    """Return a dict for a valid line, or None if the line is malformed."""
    parts = line.strip().split("|", 4)
    if len(parts) != 5:
        return None
    ts, level, service, ip, message = parts
    try:
        when = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    if level not in LEVELS:
        return None
    return {
        "time": ts,
        "hour": when.hour,
        "level": level,
        "service": service,
        "ip": ip,
        "message": message,
    }


def load_events(path):
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            event = parse_line(line)
            if event is not None:
                events.append(event)
    return events


def suggest_blocks(events, threshold):
    """IPs with at least `threshold` warnings/errors (candidates only, nothing is blocked)."""
    counts = Counter(e["ip"] for e in events if e["level"] != "INFO")
    return [{"ip": ip, "count": n} for ip, n in counts.most_common() if n >= threshold]


def summarize(events):
    levels = Counter(e["level"] for e in events)
    per_hour = [0] * 24
    for e in events:
        per_hour[e["hour"]] += 1
    bad_ips = Counter(e["ip"] for e in events if e["level"] != "INFO")
    return {
        "total": len(events),
        "levels": {level: levels.get(level, 0) for level in LEVELS},
        "unique_ips": len({e["ip"] for e in events}),
        "per_hour": per_hour,
        "top_ips": [{"ip": ip, "count": n} for ip, n in bad_ips.most_common(5)],
    }
