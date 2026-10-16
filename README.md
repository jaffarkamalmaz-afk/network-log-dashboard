# Network & Log Dashboard

A small web dashboard that reads a network/server log file and shows a summary: event counts by level, events per hour, the most suspicious IP addresses, and the latest events with a level filter.

Built with Python (Flask) and plain HTML/CSS/JavaScript.

## Run it

```bash
pip install -r requirements.txt
python generate_logs.py      # creates logs/sample.log with fake data
python app.py                # open http://127.0.0.1:5000
```

Use your own log file with `LOG_FILE=/path/to/file.log python app.py`.

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
- `log_parser.py`: log parsing and summary logic
- `generate_logs.py`: fake log generator
- `templates/`, `static/`: the web page
- `tests/`: unit tests
