import sys
from PIL import Image, ImageWin
import win32print, win32ui
import time

WIDTH = 576
MAX_HEIGHT = 3000


def print_long_image(image_path):
    printer_name = win32print.GetDefaultPrinter()
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    img = Image.open(image_path).convert("L")

    w, h = img.size
    ratio = WIDTH / w
    img = img.resize((WIDTH, int(h * ratio)))

    # 🔥 dithering vasta tässä
    img = img.convert("1", dither=Image.FLOYDSTEINBERG)

    y = 0

    hdc.StartDoc("Long Image")

    while y < img.height:
        end_y = min(y + MAX_HEIGHT, img.height)
        chunk = img.crop((0, y, WIDTH, end_y))

        if chunk.height <= 0:
            break

        dib = ImageWin.Dib(chunk)

        hdc.StartPage()
        dib.draw(hdc.GetHandleOutput(), (0, 0, chunk.width, chunk.height))
        hdc.EndPage()

        if end_y >= img.height:
            break

        y += MAX_HEIGHT
        time.sleep(0.05)

    hdc.EndDoc()
    hdc.DeleteDC()


# 🔥 TÄMÄ PUUTTUI
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
    else:
        image_path = input("Anna kuvan polku: ").strip().strip('"').strip("'")

        if image_path.startswith("&"):
            image_path = image_path.split("'", 1)[1].rsplit("'", 1)[0]

    print(f"Tulostetaan: {image_path}")
    print_long_image(image_path)