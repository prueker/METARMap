try:
	from board import SCL, SDA
	import busio
	from PIL import Image, ImageDraw, ImageFont
	import adafruit_ssd1306
	noDisplayLibraries = False
except ImportError:
	noDisplayLibraries = True

# This additional file is to support the functionality for an external display
# If you only want to have the LEDs light up, then you do not need this file

def startDisplay():
	if noDisplayLibraries:
		return None

	i2c = busio.I2C(SCL, SDA)
	disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
	disp.poweron()
	return disp
	
def shutdownDisplay(disp):
	if noDisplayLibraries:
		return

	disp.poweroff()

def clearScreen(disp):
	if noDisplayLibraries:
		return

	disp.fill(0)
	disp.show()
	
def outputMetar(disp, station, condition):
	if noDisplayLibraries:
		return

	width = disp.width
	height = disp.height
	padding = -2
	x = 0
	image = Image.new("1", (width, height))
	draw = ImageDraw.Draw(image)
	# Draw a black filled box to clear the image.
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	
	top = padding
	bottom = height - padding

	fontLarge = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 16)
	fontSmall = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 10)
	
	draw.line([(x + 62, top + 18), (x + 62, bottom)], fill=255, width=1)
	
	draw.text((x, top + 0), station + "-" + condition["flightCategory"], font=fontLarge, fill=255)
	draw.text((x + 90, top + 0), condition["obsTime"].strftime("%H:%MZ"), font=fontSmall, fill=255)
	
	draw.text((x, top + 15), condition["windDir"] + "@" + str(condition["windSpeed"]) + ("G" + str(condition["windGustSpeed"]) if condition["windGust"] else ""), font=fontSmall, fill=255)
	draw.text((x + 64, top + 15), str(condition["vis"]) + "SM " + condition["obs"], font=fontSmall, fill=255)
	draw.text((x, top + 25), str(condition["tempC"]) + "C/" + str(condition["dewpointC"]) + "C", font=fontSmall, fill=255)
	draw.text((x + 64, top + 25), "A" + str(condition["altimHg"]) + "Hg", font=fontSmall, fill=255)
	yOff = 35
	xOff = 0
	NewLine = False
	for skyIter in condition["skyConditions"]:
		draw.text((x + xOff, top + yOff), skyIter["cover"] + ("@" + str(skyIter["cloudBaseFt"]) if skyIter["cloudBaseFt"] > 0 else ""), font=fontSmall, fill=255)
		if NewLine:
			yOff += 10
			xOff = 0
			NewLine = False
		else:
			xOff = 64
			NewLine = True
	disp.image(image)
	disp.show()