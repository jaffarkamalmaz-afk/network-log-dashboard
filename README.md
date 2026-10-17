# Network & Log Dashboard

A small web dashboard that reads a network/server log file, shows a summary (event counts by level, events per hour, suspicious IP addresses, latest events), and lets you act on it: block and unblock IP addresses, with every action recorded in an audit log.

Built with Python (Flask) and plain HTML/CSS/JavaScript.

## Run it

```bash
pip install -r requirements.txt
python generate_logs.py      # creates logs/sample.log with fake data
python app.py                # open http://127.0.0.1:5000
```

Use your own log file with `LOG_FILE=/path/to/file.log python app.py`.

## Control features

- **Block / Unblock** an IP from the top-IPs table, the suggestions list or the blocklist.
- **Suggested blocks**: addresses with at least N warnings/errors (default 30). Nothing is blocked until you confirm.
- **Audit log**: who did what and when.
- **Simulated firewall**: blocking only records the address in `data/blocklist.json`. It does not touch a real firewall.
- **Safety rules**: private and local addresses (10.x, 192.168.x, 127.x ...) cannot be blocked, every action asks for confirmation, and the API only accepts JSON POST requests.

## Log format

One event per line, fields separated by `|`:

```
2026-10-16 08:15:02|WARNING|sshd|185.220.101.4|Failed password for root
```

Levels: `INFO`, `WARNING`, `ERROR`. Malformed lines are skipped.

## Tests

```bash
pip install pytest
pytest
```

## Project layout

- `app.py`: Flask routes (`/`, `/api/summary`, `/api/events`)
- `log_parser.py`: log parsing, summary and block suggestions
- `blocklist.py`: simulated firewall (blocklist + audit log)
- `generate_logs.py`: fake log generator
- `templates/`, `static/`: the web page
- `tests/`: unit tests
