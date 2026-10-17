// Fetch data from the Flask API and render it.
function el(id) { return document.getElementById(id); }

function cell(text, className) {
  var td = document.createElement("td");
  td.textContent = text;           // textContent avoids HTML injection from log data
  if (className) { td.className = className; }
  return td;
}

function buttonCell(label, className, onClick) {
  var td = document.createElement("td");
  var b = document.createElement("button");
  b.type = "button";
  b.textContent = label;
  if (className) { b.className = className; }
  b.addEventListener("click", onClick);
  td.appendChild(b);
  return td;
}

function toast(message) {
  var t = document.createElement("div");
  t.className = "toast";
  t.textContent = message;
  document.body.appendChild(t);
  setTimeout(function () { t.remove(); }, 2500);
}

function post(url, body) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  }).then(function (r) { return r.json(); });
}

function blockIp(ip, reason) {
  if (!window.confirm("Block " + ip + "?")) { return Promise.resolve(); }
  return post("/api/block", { ip: ip, reason: reason }).then(function (res) {
    toast(res.ok ? "Blocked " + ip : res.error);
    refresh();
  });
}

function unblockIp(ip) {
  if (!window.confirm("Unblock " + ip + "?")) { return; }
  post("/api/unblock", { ip: ip }).then(function (res) {
    toast(res.ok ? "Unblocked " + ip : res.error);
    refresh();
  });
}

function fillTable(id, rows, makeRow) {
  var body = el(id).querySelector("tbody");
  body.innerHTML = "";
  rows.forEach(function (row) { body.appendChild(makeRow(row)); });
}

function renderSummary(data) {
  el("c-total").textContent = data.total;
  el("c-info").textContent = data.levels.INFO;
  el("c-warning").textContent = data.levels.WARNING;
  el("c-error").textContent = data.levels.ERROR;
  el("c-ips").textContent = data.unique_ips;

  var max = Math.max.apply(null, data.per_hour.concat([1]));
  var chart = el("chart");
  chart.innerHTML = "";
  data.per_hour.forEach(function (n, hour) {
    var bar = document.createElement("div");
    bar.className = "bar";
    bar.style.height = (n / max * 100) + "%";
    bar.setAttribute("data-tip", hour + ":00 - " + n);
    chart.appendChild(bar);
  });

  fillTable("top-ips", data.top_ips, function (row) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(row.ip));
    tr.appendChild(cell(row.count));
    if (row.protected) {
      tr.appendChild(cell("protected (internal)"));
    } else if (row.blocked) {
      tr.appendChild(cell("blocked", "lv-ERROR"));
    } else {
      tr.appendChild(buttonCell("Block", "danger", function () {
        blockIp(row.ip, "Manual block from top IPs");
      }));
    }
    return tr;
  });
}

function renderEvents(events) {
  fillTable("events", events, function (e) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(e.time));
    tr.appendChild(cell(e.level, "lv-" + e.level));
    tr.appendChild(cell(e.service));
    tr.appendChild(cell(e.ip));
    tr.appendChild(cell(e.message));
    return tr;
  });
}

var suggested = [];

function renderSuggestions(list) {
  suggested = list;
  fillTable("suggest", list, function (row) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(row.ip));
    tr.appendChild(cell(row.count));
    tr.appendChild(buttonCell("Block", "danger", function () {
      blockIp(row.ip, "Suggested: " + row.count + " warnings/errors");
    }));
    return tr;
  });
  el("block-all").disabled = list.length === 0;
}

function renderBlocklist(list) {
  fillTable("blocklist", list, function (row) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(row.ip));
    tr.appendChild(cell(row.since));
    tr.appendChild(cell(row.reason));
    tr.appendChild(buttonCell("Unblock", "", function () { unblockIp(row.ip); }));
    return tr;
  });
}

function renderAudit(list) {
  fillTable("audit", list, function (a) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(a.time));
    tr.appendChild(cell(a.action));
    tr.appendChild(cell(a.ip));
    tr.appendChild(cell(a.actor));
    tr.appendChild(cell(a.detail));
    return tr;
  });
}

function getJson(url) { return fetch(url).then(function (r) { return r.json(); }); }

function refresh() {
  var level = el("level").value;
  var threshold = parseInt(el("threshold").value, 10) || 30;
  getJson("/api/summary").then(renderSummary);
  getJson("/api/events?limit=50&level=" + level).then(renderEvents);
  getJson("/api/suggestions?threshold=" + threshold).then(renderSuggestions);
  getJson("/api/blocklist").then(renderBlocklist);
  getJson("/api/audit").then(renderAudit);
  el("updated").textContent = "updated " + new Date().toLocaleTimeString();
}

el("block-all").addEventListener("click", function () {
  if (suggested.length === 0) { return; }
  if (!window.confirm("Block " + suggested.length + " suggested address(es)?")) { return; }
  var jobs = suggested.map(function (s) {
    return post("/api/block", { ip: s.ip, reason: "Auto-suggested: " + s.count + " warnings/errors" });
  });
  Promise.all(jobs).then(function () { toast("Done"); refresh(); });
});

el("level").addEventListener("change", refresh);
el("threshold").addEventListener("change", refresh);
refresh();
setInterval(refresh, 10000);
