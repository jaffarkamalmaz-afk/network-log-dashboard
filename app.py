"""Network & Log Dashboard: a small Flask app."""
import os

from flask import Flask, jsonify, render_template, request

from log_parser import LEVELS, load_events, summarize

LOG_PATH = os.environ.get("LOG_FILE", os.path.join("logs", "sample.log"))

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def api_summary():
    return jsonify(summarize(load_events(LOG_PATH)))


@app.route("/api/events")
def api_events():
    events = load_events(LOG_PATH)
    level = request.args.get("level", "").upper()
    if level in LEVELS:
        events = [e for e in events if e["level"] == level]
    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 500))
    except ValueError:
        limit = 50
    return jsonify(events[-limit:][::-1])


if __name__ == "__main__":
    app.run(debug=True)
