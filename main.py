from flask import Flask
from skyfield.api import load
import numpy as np
import os

app = Flask(__name__)

@app.route("/")
def home():
    url = 'https://celestrak.org/NORAD/elements/active.txt'
    satellites = load.tle_file(url)

    ts = load.timescale()
    now = ts.now()

    sat_points = []
    sat_paths = []

    minutes = np.linspace(0, 90, 30)

    for sat in satellites[:20]:
        positions = []

        for m in minutes:
            t = ts.utc(
                now.utc_datetime().year,
                now.utc_datetime().month,
                now.utc_datetime().day,
                now.utc_datetime().hour,
                now.utc_datetime().minute + int(m)
            )

            subpoint = sat.at(t).subpoint()

            positions.append({
                "lat": subpoint.latitude.degrees,
                "lng": subpoint.longitude.degrees
            })

        current = positions[0]

        sat_points.append({
            "name": sat.name,
            "lat": current["lat"],
            "lng": current["lng"]
        })

        sat_paths.append({
            "name": sat.name,
            "path": positions
        })

    return f"""
    <html>
    <head>
        <title>PST - Public Satellite Tracker</title>
        <script src="https://unpkg.com/three"></script>
        <script src="https://unpkg.com/globe.gl"></script>
        <style>
            body {{ margin:0; background:#020617; color:white; }}
            #globe {{ width:100vw; height:100vh; }}
        </style>
    </head>
    <body>
    <div id="globe"></div>

    <script>
        const sats = {sat_points};
        const paths = {sat_paths};

        const globe = Globe()(document.getElementById('globe'))
            .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-dark.jpg');

        globe.pointsData(sats)
            .pointLat(d => d.lat)
            .pointLng(d => d.lng)
            .pointColor(() => 'cyan');

        globe.pathsData(paths)
            .pathPoints(d => d.path)
            .pathLat(p => p.lat)
            .pathLng(p => p.lng)
            .pathColor(() => 'orange');
    </script>
    </body>
    </html>
    """

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)