import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331

def initDisplay():
    disp = SSD1331.SSD1331()
    disp.Init()

def updateDisplayReading(temp, humid, bg_color):
    disp = SSD1331.SSD1331()
    # disp.clear()


    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    fontLarge = ImageFont.truetype('./lib/oled/Font.ttf', 20)
    fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)

    print("- draw rectangle")
    draw.rectangle([(0, 0), (disp.width, disp.height)], fill=bg_color)

    draw.text((8, 0), f'temp: {temp:0.1f}', font=fontSmall, fill="WHITE")
    draw.text((12, 40), f'humid: {humid:0.1f}%', font=fontSmall, fill="WHITE")

    disp.ShowImage(image1, 0, 0)