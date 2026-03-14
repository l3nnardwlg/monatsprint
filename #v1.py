import json
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin
from pathlib import Path

# Drucker
printer_a = "Star TSP100 Cutter (TSP143)"
printer_b = "BIXOLON SRP-350plusII"

# JSON laden (script-relative path, robust handling)
data_path = Path(__file__).parent / "monat.json"
if not data_path.exists():
    print(f"Warnung: {data_path} nicht gefunden. Verwende leere Daten.")
    data = {}
else:
    try:
        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Warnung: {data_path} enthält kein gültiges JSON. Verwende leere Daten.")
        data = {}

# Anzahl Kopien
copies = int(input("Wie viele Kopien drucken? "))

# Bild erstellen (A4 Layout)
width = 800
height = 2000
img = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(img)

font_title = ImageFont.truetype("arial.ttf", 60)
font_text = ImageFont.truetype("arial.ttf", 35)

draw.text((90,20), "MONATSPLAN", fill="black", font=font_title)

y = 120

for day in range(1,10):
    day = str(day)
    if day in data:
        text = f"{day}.  {data[day]['gericht']}   {data[day]['preis']}"
    else:
        text = f"{day}.  ---"

    draw.text((20,y), text, fill="black", font=font_text)
    y += 55


def print_image(printer):
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer)

    hDC.StartDoc("Monatsplan")
    hDC.StartPage()

    dib = ImageWin.Dib(img)
    dib.draw(hDC.GetHandleOutput(), (0,0,width,height))

    hDC.EndPage()
    hDC.EndDoc()
    hDC.DeleteDC()


# Druckjobs verteilen
for i in range(copies):

    if copies > 1:
        if i % 2 == 0:
            printer = printer_a
        else:
            printer = printer_b
    else:
        printer = printer_a

    print("Drucke auf:", printer)
    print_image(printer)