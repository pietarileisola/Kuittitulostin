from PIL import Image, ImageDraw, ImageFont
import win32print, win32ui
from PIL import ImageWin

printer_name = win32print.GetDefaultPrinter()
hdc = win32ui.CreateDC()
hdc.CreatePrinterDC(printer_name)

WIDTH = 576
img = Image.new("L", (WIDTH, 400), 255)
draw = ImageDraw.Draw(img)

font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 30)

y = 10
draw.text((10, y), "KUITTI TESTI", font=font, fill=0)
y += 50

draw.text((10, y), "Kahvi        2.50€", font=font, fill=0)
y += 40
draw.text((10, y), "Croissant    3.20€", font=font, fill=0)
y += 40

draw.text((10, y), "----------------------", font=font, fill=0)
y += 40
draw.text((10, y), "YHTEENSÄ     5.70€", font=font, fill=0)

dib = ImageWin.Dib(img)

hdc.StartDoc("Receipt")
hdc.StartPage()
dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))
hdc.EndPage()
hdc.EndDoc()
hdc.DeleteDC()