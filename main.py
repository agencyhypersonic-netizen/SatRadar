from flask import Flask, jsonify, render_template_string
import requests
import random

app = Flask(__name__)

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
        data.filter(() => Math.random() > 0.95).length

    document.getElementById("alt").innerText =
        (500 + Math.floor(Math.random()*20000)) + " km"

    renderList(data)
}

function renderList(data) {
    let html = ""

    data.slice(0, 100).forEach(sat => {
        html += `
        <div class="row">
            <div class="name">${sat.name}</div>
            <div class="coords">LIVE</div>
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

/* AUTO REFRESH */
setInterval(loadData, 5000)

loadData()
</script>

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