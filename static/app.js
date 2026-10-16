// Fetch data from the Flask API and render it.
function el(id) { return document.getElementById(id); }

function cell(text, className) {
  var td = document.createElement("td");
  td.textContent = text;           // textContent avoids HTML injection from log data
  if (className) { td.className = className; }
  return td;
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

  var body = el("top-ips").querySelector("tbody");
  body.innerHTML = "";
  data.top_ips.forEach(function (row) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(row.ip));
    tr.appendChild(cell(row.count));
    body.appendChild(tr);
  });
}

function renderEvents(events) {
  var body = el("events").querySelector("tbody");
  body.innerHTML = "";
  events.forEach(function (e) {
    var tr = document.createElement("tr");
    tr.appendChild(cell(e.time));
    tr.appendChild(cell(e.level, "lv-" + e.level));
    tr.appendChild(cell(e.service));
    tr.appendChild(cell(e.ip));
    tr.appendChild(cell(e.message));
    body.appendChild(tr);
  });
}

function refresh() {
  fetch("/api/summary").then(function (r) { return r.json(); }).then(renderSummary);
  var level = el("level").value;
  fetch("/api/events?limit=50&level=" + level).then(function (r) { return r.json(); }).then(renderEvents);
  el("updated").textContent = "updated " + new Date().toLocaleTimeString();
}

el("level").addEventListener("change", refresh);
refresh();
setInterval(refresh, 10000);
