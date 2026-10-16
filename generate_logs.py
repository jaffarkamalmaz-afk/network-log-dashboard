"""Generate a synthetic network log file for testing the dashboard."""
import random
from datetime import datetime, timedelta

random.seed(7)

SERVICES = {
    "sshd": [
        ("WARNING", "Failed password for {user}"),
        ("INFO", "Accepted password for {user}"),
        ("ERROR", "Too many authentication failures for {user}"),
    ],
    "nginx": [
        ("INFO", "GET /index.html 200"),
        ("INFO", "GET /api/data 200"),
        ("WARNING", "GET /admin 403"),
        ("ERROR", "GET /login 500"),
    ],
    "firewall": [
        ("INFO", "Allowed TCP 443"),
        ("WARNING", "Blocked TCP 23"),
        ("ERROR", "Port scan detected"),
    ],
}
USERS = ["root", "admin", "ubuntu", "jaffar", "test"]
NORMAL_IPS = ["10.0.0.%d" % i for i in range(2, 12)]
SUSPICIOUS_IPS = ["185.220.101.4", "45.155.205.9", "91.240.118.22"]


def make_line(ts):
    service = random.choice(list(SERVICES))
    level, text = random.choice(SERVICES[service])
    attack = random.random() < 0.25
    ip = random.choice(SUSPICIOUS_IPS if attack else NORMAL_IPS)
    if attack and level == "INFO":
        level, text = "WARNING", "Blocked TCP 23" if service == "firewall" else text
    return "%s|%s|%s|%s|%s" % (
        ts.strftime("%Y-%m-%d %H:%M:%S"),
        level,
        service,
        ip,
        text.format(user=random.choice(USERS)),
    )


def main(path="logs/sample.log", count=600):
    start = datetime(2026, 10, 16, 0, 0, 0)
    lines = []
    for _ in range(count):
        ts = start + timedelta(seconds=random.randint(0, 24 * 3600 - 1))
        lines.append((ts, make_line(ts)))
    lines.sort()
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(line for _, line in lines) + "\n")
    print("Wrote %d lines to %s" % (count, path))


if __name__ == "__main__":
    main()
