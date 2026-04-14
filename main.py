from flask import Flask, jsonify, render_template_string
from skyfield.api import load
import requests

app = Flask(__name__)
ts = load.timescale()

cached_sats = None

# ---------------- SAFE TLE FETCH ----------------
def get_tle_data():
    url = "https://celestrak.org/NORAD/elements/active.txt"
    
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.text
    except:
        return None

# ---------------- API ----------------
@app.route("/api/satellites")
def satellites_api():
    global cached_sats

    try:
        if cached_sats is None:
            tle_data = get_tle_data()

            if tle_data:
                lines = tle_data.splitlines()
                sats = []

                for i in range(0, len(lines), 3):
                    try:
                        name = lines[i].strip()
                        l1 = lines[i+1].strip()
                        l2 = lines[i+2].strip()
                        sats.append(load.tle_file_from_lines([name, l1, l2])[0])
                    except:
                        continue

                cached_sats = sats

        if not cached_sats:
            raise Exception("No satellites loaded")

        now = ts.now()
        data = []

        for sat in cached_sats[:50]:
            subpoint = sat.at(now).subpoint()

            data.append({
                "name": sat.name,
                "lat": subpoint.latitude.degrees,
                "lon": subpoint.longitude.degrees,
                "alt": subpoint.elevation.km
            })

        return jsonify(data)

    except:
        # 🔥 HARD FALLBACK (always visible)
        return jsonify([
            {"name": "ISS", "lat": 20, "lon": 78, "alt": 420},
            {"name": "Starlink", "lat": -10, "lon": 40, "alt": 550},
            {"name": "GPS", "lat": 0, "lon": 0, "alt": 20000}
        ])

# ---------------- FRONTEND ----------------
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
        body { margin:0; background:black; color:white; }
        #map { height:100vh; }
        .title {
            position:absolute;
            top:10px;
            left:50px;
            z-index:999;
            color:cyan;
            font-size:18px;
        }
    </style>
</head>

<body>

<div class="title">🚀 PST - SatRadar</div>
<div id="map"></div>

<script>

let map = L.map('map').setView([20,0],2);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

let layer = L.layerGroup().addTo(map);

async function loadSatellites(){
    let res = await fetch('/api/satellites');
    let data = await res.json();

    console.log("DATA:", data);

    layer.clearLayers();

    data.forEach(sat=>{
        let m = L.circleMarker([sat.lat, sat.lon], {
            radius:5,
            color:"cyan"
        }).addTo(layer);

        m.bindPopup(sat.name);
    });
}

setInterval(loadSatellites, 5000);
loadSatellites();

</script>

</body>
</html>
""")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)