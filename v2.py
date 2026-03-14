from flask import Flask, request, render_template_string
import json
from pathlib import Path

import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin

app = Flask(__name__)

printer_a = "Star TSP100 Cutter (TSP143) (Kopie 1)"
printer_b = "BIXOLON SRP-350plusII"
data_path = Path(__file__).parent / "monat.json"

HTML = """
<h1>Monatsplan drucken</h1>
<form method="post">
Kopien:
<input type="number" name="copies" value="1" min="1">
<br><br>
<button type="submit">DRUCKEN</button>
</form>
"""


def load_data():
    if not data_path.exists():
        return {}

    try:
        with data_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def build_plan_image(data):
    width = 800
    line_height = 52
    title_y = 20
    start_y = 120
    height = start_y + (31 * line_height) + 60

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_title = load_font(60)
    font_text = load_font(34)

    draw.text((90, title_y), "MONATSPLAN", fill="black", font=font_title)

    y = start_y
    for day in range(1, 32):
        day_key = str(day)

        if day_key in data:
            line = f"{day}.  {data[day_key]['gericht']}   {data[day_key]['preis']}"
        else:
            line = f"{day}.  ---"

        draw.text((20, y), line, fill="black", font=font_text)
        y += line_height

    return img

def print_job(printer):
    data = load_data()
    img = build_plan_image(data)
    width, height = img.size

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer)

    hdc.StartDoc("Monatsplan")
    hdc.StartPage()

    dib = ImageWin.Dib(img)
    dib.draw(hdc.GetHandleOutput(), (0, 0, width, height))

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()

@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":
        copies = int(request.form["copies"])

        for i in range(copies):
            printer = printer_a if i % 2 == 0 else printer_b
            print_job(printer)

        return """
        <h2>Gedruckt!</h2>
        <script>
        setTimeout(()=>{window.location.href="/"},2000)
        </script>
        """

    return """
    <h1>Monatsplan drucken</h1>

    <form method="post">
        Kopien:
        <input type="number" name="copies" value="1">
        <br><br>
        <button>DRUCKEN</button>
    </form>

    <br>
    <a href="/config"><button>Monat konfigurieren</button></a>
    """
@app.route("/save", methods=["POST"])
def save():

    import json

    data = request.json

    with open("monat.json","w",encoding="utf-8") as f:
        json.dump(data,f,indent=4,ensure_ascii=False)

    return {"status":"ok"}    

@app.route("/config")
def config():

    import json

    try:
        with open("monat.json",encoding="utf-8") as f:
            data=json.load(f)
    except:
        data={}

    rows=""

    for day in range(1,32):

        gericht=data.get(str(day),{}).get("gericht","")
        preis=data.get(str(day),{}).get("preis","")

        rows+=f"""
<tr>
<td>{day}</td>
<td><input class="gericht" data-day="{day}" value="{gericht}"></td>
<td><input class="preis" data-day="{day}" value="{preis}"></td>
</tr>
"""

    return f"""
<html>

<style>

body {{
font-family:Arial;
font-size:22px;
}}

input {{
font-size:22px;
padding:8px;
width:200px;
}}

button {{
font-size:30px;
padding:20px;
margin:10px;
}}

table {{
border-collapse:collapse;
}}

td,th {{
border:1px solid #ccc;
padding:10px;
}}

</style>

<h1>Monatsplan konfigurieren</h1>

<table>

<tr>
<th>Tag</th>
<th>Gericht</th>
<th>Preis</th>
</tr>

{rows}

</table>

<br>
<a href="/"><button>Zurück</button></a>

<script>

function formatPrice(value){{
value=value.replace(",",".")
let num=parseFloat(value)

if(isNaN(num)) return value

return num.toFixed(2)
}}

function saveData(){{

let data={{}}

document.querySelectorAll(".gericht").forEach(el=>{{
let day=el.dataset.day

if(!data[day]) data[day]={{}}

data[day]["gericht"]=el.value
}})

document.querySelectorAll(".preis").forEach(el=>{{
let day=el.dataset.day

if(!data[day]) data[day]={{}}

data[day]["preis"]=formatPrice(el.value)
el.value=data[day]["preis"]
}})

fetch("/save",{{
method:"POST",
headers:{{"Content-Type":"application/json"}},
body:JSON.stringify(data)
}})
}}

document.querySelectorAll("input").forEach(el=>{{
el.addEventListener("change",saveData)
}})

</script>

</html>
"""

app.run(host="0.0.0.0", port=5000)