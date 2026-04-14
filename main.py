from flask import Flask, jsonify, render_template_string
import requests
import random

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PST - SatRadar</title>
<style>
body {
    margin:0;
    font-family: Arial;
    background: #020c1b;
    color: #00ffc3;
}

.container {
    padding: 20px;
}

.title {
    font-size: 22px;
    text-align:center;
    margin-bottom:20px;
}

.card {
    border:1px solid #00ffc3;
    border-radius:12px;
    padding:15px;
    margin-bottom:15px;
}

.big {
    font-size:28px;
    margin-top:10px;
}

.small {
    opacity:0.7;
}

input {
    width:100%;
    padding:10px;
    background:#02142b;
    border:none;
    color:#00ffc3;
    border-radius:8px;
    margin-top:10px;
}
</style>
</head>

<body>
<div class="container">

<div class="title">🛰 PST - Public Satellite Tracker</div>

<div class="card">
    <div class="small">ACTIVE TARGETS</div>
    <div id="count" class="big">...</div>
</div>

<div class="card">
    <div class="small">OVER INDIA</div>
    <div id="india" class="big">...</div>
</div>

<div class="card">
    <div class="small">AVG ALTITUDE</div>
    <div id="alt" class="big">...</div>
</div>

<div class="card">
    <div class="small">SATELLITES</div>
    <input placeholder="Search catalog..."/>
    <div id="list"></div>
</div>

</div>

<script>
fetch('/satellites')
.then(res => res.json())
.then(data => {

    document.getElementById("count").innerText = data.length;

    // fake India count (for now realistic simulation)
    document.getElementById("india").innerText = Math.floor(Math.random()*5);

    // fake avg altitude
    document.getElementById("alt").innerText = (500 + Math.floor(Math.random()*20000)) + " km";

    let html = "";

    data.slice(0, 30).forEach(sat => {
        html += `
        <p>
        ${sat.name} (${sat.id})
        </p>
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