"""Network & Log Dashboard: a small Flask app."""
import os

from flask import Flask, jsonify, render_template, request

import blocklist
from log_parser import LEVELS, load_events, suggest_blocks, summarize

LOG_PATH = os.environ.get("LOG_FILE", os.path.join("logs", "sample.log"))

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def api_summary():
    summary = summarize(load_events(LOG_PATH))
    blocked = {b["ip"] for b in blocklist.list_blocked()}
    for row in summary["top_ips"]:
        row["blocked"] = row["ip"] in blocked
        try:
            blocklist.validate_ip(row["ip"])
            row["protected"] = False
        except blocklist.BlockError:
            row["protected"] = True
    return jsonify(summary)


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


def _json_body():
    # Requiring a JSON body blocks simple cross-site form posts.
    if not request.is_json:
        return None
    return request.get_json(silent=True) or {}


def _action(fn, ip, **kwargs):
    try:
        result = fn(ip, **kwargs)
    except blocklist.BlockError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "ip": result})


@app.route("/api/blocklist")
def api_blocklist():
    return jsonify(blocklist.list_blocked())


@app.route("/api/block", methods=["POST"])
def api_block():
    body = _json_body()
    if body is None:
        return jsonify({"ok": False, "error": "JSON body required"}), 400
    return _action(blocklist.block, body.get("ip", ""), reason=str(body.get("reason", "")))


@app.route("/api/unblock", methods=["POST"])
def api_unblock():
    body = _json_body()
    if body is None:
        return jsonify({"ok": False, "error": "JSON body required"}), 400
    return _action(blocklist.unblock, body.get("ip", ""))


@app.route("/api/suggestions")
def api_suggestions():
    try:
        threshold = max(1, int(request.args.get("threshold", 30)))
    except ValueError:
        threshold = 30
    blocked = {b["ip"] for b in blocklist.list_blocked()}
    result = []
    for s in suggest_blocks(load_events(LOG_PATH), threshold):
        try:
            blocklist.validate_ip(s["ip"])
        except blocklist.BlockError:
            continue  # never suggest private or local addresses
        if s["ip"] not in blocked:
            result.append(s)
    return jsonify(result)


@app.route("/api/audit")
def api_audit():
    return jsonify(blocklist.read_audit())


if __name__ == "__main__":
    app.run(debug=True)
