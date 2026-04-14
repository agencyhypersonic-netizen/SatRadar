from flask import Flask, jsonify
from skyfield.api import load
import os

app = Flask(__name__)

ts = load.timescale()
satellites = load.tle_file('https://celestrak.org/NORAD/elements/active.txt')

@app.route("/api/satellites")
def satellites_api():
    now = ts.now()
    data = []

    for sat in satellites[:50]:
        geocentric = sat.at(now)
        subpoint = geocentric.subpoint()

        data.append({
            "name": sat.name,
            "lat": subpoint.latitude.degrees,
            "lon": subpoint.longitude.degrees,
            "alt": subpoint.elevation.km
        })

    return jsonify(data)


@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>PST - SatRadar</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>

<style>
body { margin:0; background:#0a0f1c; color:white; font-family:Arial;}
#map { height:100vh; }
.title {
    position:absolute;
    top:10px;
    left:10px;
    z-index:1000;
    font-size:18px;
}
</style>
</head>

<body>

<div class="title">🛰 PST - Public Satellite Tracker</div>
<div id="map"></div>

<script>
var map = L.map('map').setView([20, 0], 2);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

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
            "Lon: " + sat.lon.toFixed(2)
        );

        markers.push(marker);
    });
}

setInterval(loadSatellites, 5000);
loadSatellites();
</script>

</body>
</html>
"""

# Render PORT fix
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)