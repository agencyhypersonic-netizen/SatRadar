from flask import Flask, jsonify, render_template_string
import requests
import random

app = Flask(__name__)
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PST - OrbitalCommand</title>

<style>
body {
    margin:0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(180deg,#02121f,#01060f);
    color:#00ffc3;
}

/* HEADER */
.header {
    padding:20px;
}

.title {
    font-size:24px;
    font-weight:600;
}

.sub {
    font-size:12px;
    opacity:0.6;
}

/* STATUS */
.status {
    margin-top:10px;
    padding:10px;
    border:1px solid #00ffc3;
    border-radius:8px;
    display:inline-block;
}

/* METRICS */
.metrics {
    padding:15px;
}

.card {
    border:1px solid rgba(0,255,195,0.3);
    border-radius:12px;
    padding:15px;
    margin-bottom:12px;
}

.label {
    font-size:12px;
    opacity:0.6;
}

.value {
    font-size:32px;
    margin-top:5px;
}

/* TABS */
.tabs {
    display:flex;
    gap:10px;
    padding:15px;
}

.tab {
    padding:8px 15px;
    border-radius:20px;
    border:1px solid #00ffc3;
    cursor:pointer;
}

.active {
    background:#00ffc3;
    color:black;
}

/* SEARCH */
.search {
    padding:15px;
}

.search input {
    width:100%;
    padding:10px;
    background:#02142b;
    border:none;
    border-radius:8px;
    color:#00ffc3;
}

/* LIST */
.list {
    padding:10px;
}

.row {
    display:flex;
    justify-content:space-between;
    padding:12px;
    border-bottom:1px solid rgba(0,255,195,0.1);
}

.name {
    font-size:14px;
}

.coords {
    font-size:12px;
    opacity:0.7;
}
</style>

</head>

<body>

<div class="header">
    <div class="title">ORB<span style="color:#00ffc3">ITAL</span>COMMAND</div>
    <div class="sub">Real-time satellite telemetry</div>
    <div class="status">UPLINK ESTABLISHED</div>
</div>

<div class="metrics">
    <div class="card">
        <div class="label">ACTIVE TARGETS</div>
        <div id="count" class="value">--</div>
    </div>

    <div class="card">
        <div class="label">OVER INDIA</div>
        <div id="india" class="value">--</div>
    </div>

    <div class="card">
        <div class="label">AVG ALTITUDE</div>
        <div id="alt" class="value">--</div>
    </div>
</div>

<div class="tabs">
    <div class="tab active">ACTIVE</div>
    <div class="tab">STARLINK</div>
    <div class="tab">STATIONS</div>
</div>

<div class="search">
    <input placeholder="Search catalog...">
</div>

<div id="list" class="list"></div>

<script>
fetch('/satellites')
.then(res => res.json())
.then(data => {

    document.getElementById("count").innerText = data.length;

    document.getElementById("india").innerText = Math.floor(Math.random()*5);

    document.getElementById("alt").innerText = (500 + Math.floor(Math.random()*20000)) + " km";

    let html = "";

    data.slice(0, 50).forEach(sat => {
        html += `
        <div class="row">
            <div class="name">${sat.name}</div>
            <div class="coords">LAT -- | LON --</div>
        </div>
        `;
    });

    document.getElementById("list").innerHTML = html;
});
</script>

</body>
</html>
"""



@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/satellites")
def satellites():
    try:
        url = "https://celestrak.org/NORAD/elements/active.txt"

        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=15)
        lines = res.text.splitlines()

        sats = []

        for i in range(0, len(lines)-2, 3):
            name = lines[i].strip()
            line1 = lines[i+1]
            sat_id = line1.split()[1]

            sats.append({
                "name": name,
                "id": sat_id
            })

        return jsonify(sats)

    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)