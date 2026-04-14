from flask import Flask, jsonify, render_template_string
import requests
from sgp4.api import Satrec, jday
import datetime

app = Flask(__name__)

# ----------- CACHE -----------
TLE_CACHE = []
LAST_FETCH = None

# ----------- FETCH TLE -----------
def fetch_tle():
    global TLE_CACHE, LAST_FETCH

    if LAST_FETCH:
        return TLE_CACHE  # reuse cache (Render safe)

    try:
        url = "https://celestrak.org/NORAD/elements/active.txt"
        r = requests.get(url, timeout=10)
        lines = r.text.splitlines()

        sats = []
        for i in range(0, len(lines), 3):
            try:
                name = lines[i].strip()
                l1 = lines[i+1].strip()
                l2 = lines[i+2].strip()

                sat = Satrec.twoline2rv(l1, l2)
                sats.append((name, sat))
            except:
                continue

        TLE_CACHE = sats
        LAST_FETCH = True
        return sats

    except:
        return []

# ----------- COMPUTE POSITION -----------
def get_positions():
    sats = fetch_tle()

    now = datetime.datetime.utcnow()
    jd, fr = jday(now.year, now.month, now.day,
                  now.hour, now.minute, now.second)

    data = []

    for name, sat in sats[:100]:
        try:
            e, r, v = sat.sgp4(jd, fr)

            if e == 0:
                lat = r[0] % 90
                lon = r[1] % 180

                data.append({
                    "name": name,
                    "lat": float(lat),
                    "lon": float(lon),
                    "alt": round(r[2], 2)
                })
        except:
            continue

    return data

# ----------- API -----------
@app.route("/api/satellites")
def api():
    data = get_positions()

    if not data:
        return jsonify([
            {"name": "Fallback-1", "lat": 20, "lon": 78, "alt": 500},
            {"name": "Fallback-2", "lat": -10, "lon": 40, "alt": 600}
        ])

    return jsonify(data)

# ----------- FRONTEND -----------
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>PST - SatRadar</title>

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
body { margin:0; background:#050b1a; color:white; font-family:Arial; }
#map { height:60vh; }

.panel {
    padding:15px;
}

.title {
    color:#00ffc3;
    font-size:24px;
}

.card {
    background:#0b1a2e;
    padding:15px;
    margin-top:10px;
    border-radius:10px;
}

.big {
    font-size:28px;
    color:#00ffc3;
}
</style>
</head>

<body>

<div id="map"></div>

<div class="panel">
    <div class="title">ORBITAL COMMAND</div>

    <div class="card">
        ACTIVE TARGETS<br>
        <div class="big" id="count">0</div>
    </div>
</div>

<script>

let map = L.map('map').setView([20,0],2);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

let layer = L.layerGroup().addTo(map);

async function loadSatellites(){
    let res = await fetch('/api/satellites');
    let data = await res.json();

    document.getElementById("count").innerText = data.length;

    layer.clearLayers();

    data.forEach(sat=>{
        let m = L.circleMarker([sat.lat, sat.lon], {
            radius:4,
            color:"#00ffc3"
        }).addTo(layer);

        m.bindPopup(
            "<b>"+sat.name+"</b><br>"+
            "Alt: "+sat.alt+" km"
        );
    });
}

setInterval(loadSatellites, 5000);
loadSatellites();

</script>

</body>
</html>
""")

# ----------- RUN -----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)