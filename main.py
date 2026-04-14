from flask import Flask, jsonify, render_template_string
from skyfield.api import load
import traceback

app = Flask(__name__)

# Load timescale
ts = load.timescale()

# Cache satellites
cached_sats = None

# ---------------- API ----------------
@app.route("/api/satellites")
def satellites_api():
    global cached_sats

    try:
        if cached_sats is None:
            url = 'https://celestrak.org/NORAD/elements/active.txt'
            cached_sats = load.tle_file(url)

        now = ts.now()
        data = []

        for sat in cached_sats[:50]:
            geocentric = sat.at(now)
            subpoint = geocentric.subpoint()

            data.append({
                "name": sat.name,
                "lat": subpoint.latitude.degrees,
                "lon": subpoint.longitude.degrees,
                "alt": subpoint.elevation.km
            })

        return jsonify(data)

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

        # fallback (always show something)
        return jsonify([
            {"name": "ISS (demo)", "lat": 20, "lon": 78, "alt": 420},
            {"name": "Starlink (demo)", "lat": -10, "lon": 40, "alt": 550}
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
        body {
            margin: 0;
            background: black;
            color: white;
            font-family: Arial;
        }

        #map {
            height: 100vh;
            width: 100%;
        }

        .title {
            position: absolute;
            top: 10px;
            left: 50px;
            z-index: 999;
            font-size: 20px;
            color: cyan;
        }
    </style>
</head>

<body>

<div class="title">🚀 PST - SatRadar</div>
<div id="map"></div>

<script>

let map = L.map('map').setView([20, 0], 2);

// Dark map
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

// Satellite layer
let satLayer = L.layerGroup().addTo(map);

async function loadSatellites() {
    try {
        let res = await fetch('/api/satellites');
        console.log("API STATUS:", res.status);

        let data = await res.json();
        console.log("SAT DATA:", data);

        satLayer.clearLayers();

        data.forEach(sat => {
            let marker = L.circleMarker([sat.lat, sat.lon], {
                radius: 4,
                color: "cyan"
            }).addTo(satLayer);

            marker.bindPopup(
                "<b>" + sat.name + "</b><br>" +
                "Lat: " + sat.lat.toFixed(2) + "<br>" +
                "Lon: " + sat.lon.toFixed(2) + "<br>" +
                "Alt: " + sat.alt.toFixed(2) + " km"
            );
        });

    } catch (e) {
        console.error("FETCH ERROR:", e);
    }
}

// Refresh every 5 sec
setInterval(loadSatellites, 5000);
loadSatellites();

</script>

</body>
</html>
""")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)