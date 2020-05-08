#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET
import board
import neopixel

# NeoPixel LED Configuration
LED_COUNT		= 30					# Number of LED pixels.
LED_PIN			= board.D18				# GPIO pin connected to the pixels (18 is PCM).
LED_BRIGHTNESS		= 0.5					# Float from 0.0 (min) to 1.0 (max)
LED_ORDER		= neopixel.GRB				# Strip type and colour ordering

COLOR_VFR		= (255,0,0)				# Green
COLOR_MVFR		= (0,0,255)				# Blue
COLOR_IFR		= (0,255,0)				# Red
COLOR_LIFR		= (0,125,125)				# Magenta
COLOR_CLEAR		= (0,0,0)				# Clear
# Initialize the LED strip
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = LED_BRIGHTNESS, pixel_order = LED_ORDER, auto_write = False)

# Read the airports file to retrieve list of airports and use as order for LEDs
with open("/home/pi/airports") as f:
	airports = f.readlines()
airports = [x.strip() for x in airports]

# Retrieve METAR from aviationweather.gov data server
# Details about parameters can be found here: https://www.aviationweather.gov/dataserver/example?datatype=metar
url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + ",".join([item for item in airports if item != "NULL"])
print(url)

content = urllib.request.urlopen(url).read()

# Retrieve flying conditions from the service response and store in a dictionary for each airport
root = ET.fromstring(content)
conditionDict = { "":"" }
for metar in root.iter('METAR'):
	stationId = metar.find('station_id').text
	if metar.find('flight_category') is None:
		print("Missing flight condition, skipping.")
		continue
	flightCateory = metar.find('flight_category').text
	conditionDict[stationId] = flightCateory

# Setting LED colors based on weather conditions
i = 0
for airportcode in airports:
	# Skip NULL entries
	if airportcode == "NULL":
		i += 1
		continue
	
	color = COLOR_CLEAR
	flightCateory = conditionDict.get(airportcode,"No")
	
	if  flightCateory != "No":
		if flightCateory == "VFR":
			color = COLOR_VFR
		elif flightCateory == "MVFR":
			color = COLOR_MVFR
		elif flightCateory == "IFR":
			color = COLOR_IFR
		elif flightCateory == "LIFR":
			color = COLOR_LIFR
		else:
			color = COLOR_CLEAR
	
	print()
	print("Setting LED " + str(i) + " for " + airportcode + " to " + flightCateory + " " + str(color))
	pixels[i] = color
	i += 1

# Update actual LEDs all at once
pixels.show()

print()
print("Done")

