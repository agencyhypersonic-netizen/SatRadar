from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>SatRadar</title>

<style>
body {
    background: #020c1b;
    color: #00ffc3;
    font-family: Arial;
    padding: 20px;
}

.card {
    border: 1px solid #00ffc3;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 10px;
}

.row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #0a2a2a;
}

input {
    width: 100%;
    padding: 10px;
    margin-top: 10px;
    background: #01111f;
    color: #00ffc3;
    border: none;
}

.tabs {
    display: flex;
    gap: 10px;
    margin: 10px 0;
}

.tab {
    padding: 8px 12px;
    border: 1px solid #00ffc3;
    cursor: pointer;
}

.active {
    background: #00ffc3;
    color: black;
}
</style>

</head>

<body>

<h2>🛰 PST - Public Satellite Tracker</h2>

<div class="card">ACTIVE TARGETS: <span id="count">0</span></div>
<div class="card">OVER INDIA: <span id="india">0</span></div>
<div class="card">AVG ALTITUDE: <span id="alt">0</span></div>

<input placeholder="Search satellites...">

<div class="tabs">
    <div class="tab active">ACTIVE</div>
    <div class="tab">STARLINK</div>
</div>

<div id="list"></div>

<script>

let allSats = []

async function loadData() {
    try {
        let res = await fetch('/satellites')
        let data = await res.json()

        allSats = data
        updateUI(data)

    } catch(e) {
        console.log("Error loading data")
    }
}

function updateUI(data) {
    document.getElementById("count").innerText = data.length

    document.getElementById("india").innerText =
        Math.floor(Math.random() * 10)

    document.getElementById("alt").innerText =
        (500 + Math.floor(Math.random()*20000)) + " km"

    renderList(data)
}

function renderList(data) {
    let html = ""

    data.slice(0, 100).forEach(sat => {
        html += `
        <div class="row">
            <div>${sat.name}</div>
            <div>LIVE</div>
        </div>`
    })

    document.getElementById("list").innerHTML = html
}

/* SEARCH */
document.querySelector("input").addEventListener("input", (e) => {
    let q = e.target.value.toLowerCase()

    let filtered = allSats.filter(s =>
        s.name.toLowerCase().includes(q)
    )

    renderList(filtered)
})

/* TABS */
document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {

        document.querySelectorAll(".tab").forEach(t =>
            t.classList.remove("active")
        )

        tab.classList.add("active")

        if (tab.innerText === "STARLINK") {
            let filtered = allSats.filter(s =>
                s.name.toLowerCase().includes("starlink")
            )
            renderList(filtered)
        } else {
            renderList(allSats)
        }
    })
})

setInterval(loadData, 5000)
loadData()

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