import time
import datetime
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(board.SCL, board.SDA)

disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

disp.fill(0)
disp.show()

width = disp.width
height = disp.height

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

# Black box to clear image
def clear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(image)

# Load font
font = ImageFont.truetype('font.tff', 16)

while True:
    clear()
    draw.text((0, 4), datetime.datetime.now().strftime('%a %H:%M:%S'), font=font, fill=255)
    disp.image(image)
    disp.show()
    time.sleep(0.5)
