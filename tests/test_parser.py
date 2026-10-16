import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_parser import parse_line, summarize  # noqa: E402


def test_valid_line():
    e = parse_line("2026-10-16 08:15:02|WARNING|sshd|1.2.3.4|Failed password for root")
    assert e["level"] == "WARNING" and e["hour"] == 8 and e["ip"] == "1.2.3.4"


def test_malformed_lines_are_skipped():
    assert parse_line("garbage") is None
    assert parse_line("bad-time|INFO|sshd|1.2.3.4|x") is None
    assert parse_line("2026-10-16 08:15:02|DEBUG|sshd|1.2.3.4|x") is None


def test_summary_counts():
    events = [
        parse_line("2026-10-16 01:00:00|INFO|nginx|10.0.0.2|ok"),
        parse_line("2026-10-16 01:05:00|ERROR|nginx|9.9.9.9|boom"),
        parse_line("2026-10-16 02:00:00|WARNING|sshd|9.9.9.9|fail"),
    ]
    s = summarize(events)
    assert s["total"] == 3 and s["levels"]["ERROR"] == 1
    assert s["per_hour"][1] == 2 and s["top_ips"][0] == {"ip": "9.9.9.9", "count": 2}
