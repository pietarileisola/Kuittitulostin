import random
import os
from PIL import Image, ImageDraw, ImageFont
import win32print
import win32ui
from PIL import ImageWin

KANJI_FILE = "kanjiN5.txt"
USED_FILE = "used_kanji.txt"

WIDTH = 576
MARGIN = 20

# ---------- DATA ----------
def load_kanji():
    with open(KANJI_FILE, "r", encoding="utf-8") as f:
        return [k.strip() for k in f.readlines() if k.strip()]

def load_used():
    if not os.path.exists(USED_FILE):
        return []
    with open(USED_FILE, "r", encoding="utf-8") as f:
        return [k.strip() for k in f.readlines()]

def save_used(kanji):
    with open(USED_FILE, "a", encoding="utf-8") as f:
        f.write(kanji + "\n")

def pick_kanji():
    all_kanji = load_kanji()
    used = load_used()
    remaining = [k for k in all_kanji if k not in used]

    if not remaining:
        print("Kaikki kanjit käytetty 😄")
        return None

    return random.choice(remaining)

# ---------- TEXT ----------
def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        w = draw.textbbox((0, 0), test, font=font)[2]

        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_block(draw, text, font, y, align="left"):
    lines = wrap_text(text, font, WIDTH - 2 * MARGIN, draw)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if align == "center":
            x = (WIDTH - w) // 2
        else:
            x = MARGIN

        draw.text((x, y), line, font=font, fill=0)
        y += h + 8

    return y


def draw_separator(draw, y):
    draw.line((MARGIN, y, WIDTH - MARGIN, y), fill=0, width=2)
    return y + 20


# ---------- PRINT ----------
def print_kanji(kanji):
    printer_name = win32print.GetDefaultPrinter()
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    # iso canvas (leikataan lopuksi)
    img = Image.new('L', (WIDTH, 2000), 255)
    draw = ImageDraw.Draw(img)

    # fontit
    small = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 48)
    medium = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 70)
    big = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 220)

    y = 20

    # HEADER
    y = draw_block(draw, "今日の漢字", medium, y, align="center")
    y = draw_separator(draw, y)

    # KANJI (center)
    bbox = draw.textbbox((0, 0), kanji, font=big)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (WIDTH - w) // 2
    draw.text((x, y), kanji, font=big, fill=0)
    y += h + 30

    y = draw_separator(draw, y)

    # INFO
    text = "Meaning: day / sun. This is a " \
    "longer explanation that demonstrates automatic " \
    "text wrapping and layout consistency."

    y = draw_block(draw, text, small, y)

    # FOOTER
    y += 20
    y = draw_separator(draw, y)
    y = draw_block(draw, "Keep going. One kanji a day.", small, y, align="center")

    # crop
    img = img.crop((0, 0, WIDTH, y + 20))

    # print
    dib = ImageWin.Dib(img)

    hdc.StartDoc("Kanji")
    hdc.StartPage()
    dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()


# ---------- MAIN ----------
def main():
    input("Paina Enter tulostaaksesi kanjin...")

    kanji = pick_kanji()
    if kanji:
        print(f"Tulostetaan: {kanji}")
        print_kanji(kanji)
        save_used(kanji)


if __name__ == "__main__":
    main()