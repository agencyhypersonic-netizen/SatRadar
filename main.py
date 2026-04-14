from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

# HTML UI (clean + dark like your Replit design)
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PST - SatRadar</title>
<style>
body {
    margin:0;
    font-family: Arial;
    background: #050d1a;
    color: #00ffc3;
}
h1 {
    text-align:center;
    margin-top:20px;
}
.card {
    margin:20px;
    padding:15px;
    border:1px solid #00ffc3;
    border-radius:10px;
}
</style>
</head>
<body>

<h1>🛰 PST - Public Satellite Tracker</h1>

<div class="card">
    <h3>Active Satellites</h3>
    <div id="count">Loading...</div>
</div>

<div class="card">
    <h3>Satellite List</h3>
    <div id="list"></div>
</div>

<script>
fetch('/satellites')
.then(res => res.json())
.then(data => {
    document.getElementById('count').innerText = data.length;

    let html = "";
    data.slice(0, 50).forEach(sat => {
        html += `<p>${sat.name} (${sat.id})</p>`;
    });

    document.getElementById('list').innerHTML = html;
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
        data = requests.get(url, timeout=10).text.splitlines()

        sats = []
        for i in range(0, len(data), 3):
            name = data[i].strip()
            line1 = data[i+1]
            sat_id = line1.split()[1]

            sats.append({
                "name": name,
                "id": sat_id
            })

        return jsonify(sats)

    except:
        return jsonify([{"name": "ERROR FETCHING DATA", "id": "0"}])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)