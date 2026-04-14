from flask import Flask, jsonify, render_template_string
from skyfield.api import load
import numpy as np
import os

app = Flask(__name__)

# Load satellites
url = 'https://celestrak.org/NORAD/elements/active.txt'
satellites = load.tle_file(url)

ts = load.timescale()

@app.route("/api/satellites")
def get_satellites():
    now = ts.now()
    sat_data = []

    for sat in satellites[:100]:  # limit for performance
        geocentric = sat.at(now)
        subpoint = geocentric.subpoint()

        sat_data.append({
            "name": sat.name,
            "lat": subpoint.latitude.degrees,
            "lon": subpoint.longitude.degrees,
            "alt": subpoint.elevation.km
        })

    return jsonify(sat_data)


@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>PST - SatRadar</title>
<script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"/>

<style>
body { margin:0; background:#0a0f1c; color:white; font-family:Arial;}
#map { height:100vh; }
.title {
    position:absolute;
    top:10px;
    left:10px;
    z-index:1000;
    font-size:20px;
    font-weight:bold;
}
</style>
</head>

<body>

<div class="title">🛰 PST - Public Satellite Tracker</div>
<div id="map"></div>

<script>
var map = L.map('map').setView([20, 0], 2);

// Dark map
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap'
}).addTo(map);

let markers = [];

async function loadSatellites() {
    let res = await fetch('/api/satellites');
    let data = await res.json();

    markers.forEach(m => map.removeLayer(m));
    markers = [];

    data.forEach(sat => {
        let marker = L.circleMarker([sat.lat, sat.lon], {
            radius: 4,
            color: "#00ffe1"
        }).addTo(map);

        marker.bindPopup(
            "<b>" + sat.name + "</b><br>" +
            "Lat: " + sat.lat.toFixed(2) + "<br>" +
            "Lon: " + sat.lon.toFixed(2) + "<br>" +
            "Alt: " + sat.alt.toFixed(2) + " km"
        );

        markers.push(marker);
    });
}

// refresh every 5 sec
setInterval(loadSatellites, 5000);
loadSatellites();
</script>

</body>
</html>
""")


# 🔥 IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)