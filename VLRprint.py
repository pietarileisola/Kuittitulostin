import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont, ImageWin
import win32print, win32ui


# ---------------- FETCH ----------------
def fetch_vct_matches():
    url = "https://www.vlr.gg/matches"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    matches = soup.find_all("a", class_="match-item")

    result = []

    now = datetime.now()
    limit = now + timedelta(hours=24)

    for m in matches:
        teams = m.find_all("div", class_="match-item-vs-team-name")
        if len(teams) != 2:
            continue

        t1 = teams[0].text.strip()
        t2 = teams[1].text.strip()

        if t1 == "TBD" or t2 == "TBD":
            continue

        time_div = m.find("div", class_="match-item-time")
        time_text = time_div.text.strip() if time_div else ""

        event = m.find("div", class_="match-item-event")
        event_text = event.text.strip() if event else ""
        event_text = " ".join(event_text.split())

        if "VCT" not in event_text:
            continue

        # region
        if "Americas" in event_text:
            region = "AMERICAS"
        elif "EMEA" in event_text:
            region = "EMEA"
        elif "Pacific" in event_text:
            region = "PACIFIC"
        elif "China" in event_text:
            region = "CHINA"
        else:
            region = "OTHER"

        # parse time
        try:
            match_time = datetime.strptime(time_text, "%I:%M %p")

            match_time = match_time.replace(
                year=now.year,
                month=now.month,
                day=now.day
            )

            if match_time < now:
                match_time += timedelta(days=1)

        except:
            continue

        # 24h filter
        if not (now <= match_time <= limit):
            continue

        result.append({
            "team1": t1,
            "team2": t2,
            "time": match_time.strftime("%H:%M"),
            "region": region,
            "datetime": match_time
        })

    # 🔥 järjestä ajallisesti
    result.sort(key=lambda x: x["datetime"])

    return result


# ---------------- PRINT ----------------
def print_vlr_schedule(matches):
    WIDTH = 576
    img = Image.new("L", (WIDTH, 3000), 255)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 34)
    title_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 48)

    y = 20

    # HEADER
    draw.text((20, y), "VCT NEXT 24H", font=title_font, fill=0)
    y += 60
    draw.text((20, y), "────────────", font=font, fill=0)
    y += 50

    # group by region
    grouped = {}
    for m in matches:
        grouped.setdefault(m["region"], []).append(m)

    for region, games in grouped.items():
        draw.text((20, y), f"[{region}]", font=font, fill=0)
        y += 40

        for m in games:
            draw.text((20, y), f"{m['team1']} vs {m['team2']}", font=font, fill=0)
            y += 35
            draw.text((20, y), m["time"], font=font, fill=0)
            y += 45

        y += 15

    # jos ei matseja
    if not matches:
        draw.text((20, y), "No matches in next 24h", font=font, fill=0)

    # crop
    img = img.crop(img.getbbox())

    # print
    printer_name = win32print.GetDefaultPrinter()
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    dib = ImageWin.Dib(img)

    hdc.StartDoc("VLR")
    hdc.StartPage()
    dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()


# ---------------- RUN ----------------
matches = fetch_vct_matches()
print_vlr_schedule(matches)