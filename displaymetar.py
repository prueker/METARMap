try:
	from board import SCL, SDA
	import busio
	from PIL import Image, ImageDraw, ImageFont
	import adafruit_ssd1306
	import time
	from pytz import timezone
	import pytz
	noDisplayLibraries = False
except ImportError:
	noDisplayLibraries = True

# This additional file is to support the functionality for an external display
# If you only want to have the LEDs light up, then you do not need this file

fontLarge = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 20)
fontMed = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
fontSmall = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 12)

padding = -3
x = 0

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
	

def outputMetar1(disp, station, condition):
	if noDisplayLibraries:
		return
	
	width = disp.width
	height = disp.height
	image1 = Image.new("1", (width, height))
	draw1 = ImageDraw.Draw(image1)
	# Draw a black filled box to clear the image.
	draw1.rectangle((0, 0, width, height), outline=0, fill=0)
	
	top = padding
	bottom = height - padding
	
	#draw.line([(x + 85, top + 18), (x + 85, bottom)], fill=255, width=1)
	central = timezone('US/Central')
	draw1.text((x, top + 0), station + "-" + condition["flightCategory"], font=fontLarge, fill=255)
	draw1.text((x, top + 20), condition["windDir"] + "@" + str(condition["windSpeed"]) + (("G" + str(condition["windGustSpeed"]) if condition["windGust"] else "") + "/" +str(condition["vis"]) + "SM "), font=fontMed, fill=255)
	draw1.text((x, top + 35), str(condition["altimHg"]) + "Hg" + " " + str(condition["tempC"]) + "/" + str(condition["dewpointC"]) + "C", font=fontMed, fill=255)
	draw1.text((x, top + 50), condition["obsTime"].astimezone(central).strftime("%H:%MC") + " " + condition["obsTime"].strftime("%H:%MZ"), font=fontSmall, fill=255)
	disp.image(image1)
	disp.show()
	
def outputMetar2(disp, station, condition):
	if noDisplayLibraries:
		return
	
	width = disp.width
	height = disp.height
	image2 = Image.new("1", (width, height))
	draw2 = ImageDraw.Draw(image2)
	# Draw a black filled box to clear the image.
	draw2.rectangle((0, 0, width, height), outline=0, fill=0)
	
	top = padding
	bottom = height - padding
	
	draw2.rectangle((0, 0, width, height), outline=0, fill=0)
	draw2.text((x, top + 0), station + "-" + condition["flightCategory"], font=fontLarge, fill=255)	
	yOff = 18
	xOff = 0
	NewLine = False
	for skyIter in condition["skyConditions"]:
		draw2.text((x + xOff, top + yOff), skyIter["cover"] + ("@" + str(skyIter["cloudBaseFt"]) if skyIter["cloudBaseFt"] > 0 else ""), font=fontSmall, fill=255)
		if NewLine:
			yOff += 12
			xOff = 0
			NewLine = False
		else:
			xOff = 65
			NewLine = True
	draw2.text((x, top + 50), condition["obs"], font=fontMed, fill=255)
	disp.image(image2)
	disp.show()