from flask import Flask, render_template_string
import subprocess
import sys

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI Signal Scanner</title>
<meta http-equiv="refresh" content="15">

<style>
body{
background:#111;
color:white;
font-family:Arial;
padding:20px;
}

h1{
color:#00ff99;
}

.best{
background:#222;
padding:15px;
margin-bottom:20px;
border:2px solid #00ff99;
}

table{
width:100%;
border-collapse:collapse;
font-size:14px;
}

th,td{
border:1px solid #333;
padding:8px;
text-align:center;
}

th{
background:#222;
}

.buy{
color:lime;
font-weight:bold;
}

.sell{
color:red;
font-weight:bold;
}

.wait{
color:orange;
font-weight:bold;
}
</style>
</head>

<body>

<h1>AI Signal Scanner</h1>

<div class="best">
<h2>🔥 BEST SIGNAL</h2>
<p>{{ best }}</p>
</div>

<table>

<tr>
<th>Pair</th>
<th>Signal</th>
<th>RSI</th>
<th>Pattern</th>
<th>Confidence</th>
<th>Strength</th>
<th>Entry</th>
<th>Countdown</th>
<th>Volatility</th>
<th>Support</th>
<th>Resistance</th>
<th>Expiry</th>
</tr>

{% for row in rows %}
<tr>
<td>{{ row.pair }}</td>
<td class="{{ row.signal.lower() }}">{{ row.signal }}</td>
<td>{{ row.rsi }}</td>
<td>{{ row.pattern }}</td>
<td>{{ row.confidence }}</td>
<td>{{ row.strength }}</td>
<td>{{ row.entry }}</td>
<td>{{ row.countdown }}</td>
<td>{{ row.volatility }}</td>
<td>{{ row.support }}</td>
<td>{{ row.resistance }}</td>
<td>{{ row.expiry }}</td>
</tr>
{% endfor %}

</table>

</body>
</html>
"""

@app.route("/")
def home():

    rows = []

    try:

        result = subprocess.run(
            [sys.executable, "scanner.py"],
            capture_output=True,
            text=True
        )

        output = result.stdout

    except Exception as e:

        output = f"ERROR: {e}"

    best = "No Strong Signal"
    best_conf = -1

    for line in output.splitlines():

        if "Signal:" not in line:
            continue

        parts = [x.strip() for x in line.split("|")]

        if len(parts) < 12:
            continue

        try:

            pair = parts[0]
            signal = parts[1].replace("Signal:", "").strip()
            rsi = parts[2].replace("RSI:", "").strip()
            pattern = parts[3].replace("Pattern:", "").strip()
            confidence = parts[4].replace("Confidence:", "").strip()
            strength = parts[5].replace("Strength:", "").strip()
            entry = parts[6].replace("Entry:", "").strip()
            countdown = parts[7].replace("Countdown:", "").strip()
            volatility = parts[8].replace("Volatility:", "").strip()
            support = parts[9].replace("Support:", "").strip()
            resistance = parts[10].replace("Resistance:", "").strip()
            expiry = parts[11].replace("Expiry:", "").strip()

            try:
                conf_num = int(confidence.replace("%", ""))
            except:
                conf_num = 0

            if signal != "WAIT" and conf_num > best_conf:
                best_conf = conf_num
                best = f"{pair} | {signal} | {confidence} | Entry {entry}"

            rows.append({
                "pair": pair,
                "signal": signal,
                "rsi": rsi,
                "pattern": pattern,
                "confidence": confidence,
                "strength": strength,
                "entry": entry,
                "countdown": countdown,
                "volatility": volatility,
                "support": support,
                "resistance": resistance,
                "expiry": expiry
            })

        except:
            pass

    return render_template_string(
        HTML,
        rows=rows,
        best=best
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)