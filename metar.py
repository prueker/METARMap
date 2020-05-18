#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET
import board
import neopixel
import time

# NeoPixel LED Configuration
LED_COUNT			= 30				# Number of LED pixels.
LED_PIN				= board.D18			# GPIO pin connected to the pixels (18 is PCM).
LED_BRIGHTNESS			= 0.5				# Float from 0.0 (min) to 1.0 (max)
LED_ORDER			= neopixel.GRB			# Strip type and colour ordering

COLOR_VFR		= (255,0,0)			# Green
COLOR_VFR_FADE		= (125,0,0)			# Green Fade for wind
COLOR_MVFR		= (0,0,255)			# Blue
COLOR_MVFR_FADE		= (0,0,125)			# Blue Fade for wind
COLOR_IFR		= (0,255,0)			# Red
COLOR_IFR_FADE		= (0,125,0)			# Red Fade for wind
COLOR_LIFR		= (0,125,125)			# Magenta
COLOR_LIFR_FADE		= (0,75,75)			# Magenta Fade for wind
COLOR_CLEAR		= (0,0,0)			# Clear
COLOR_LIGHTNING		= (255,255,255)			# White

# Do you want the METARMap to be static to just show flight conditions, or do you also want blinking/fading based on current wind conditions
ACTIVATE_WINDCONDITION_ANIMATION = False			# Set this to False for Static or True for animated wind conditions

#Do you want the Map to Flash white for lightning in the area
ACTIVATE_LIGHTNING_ANIMATION = False			# Set this to False for Static or True for animated Lightning

# Fade instead of blink
FADE_INSTEAD_OF_BLINK	= True				# Set to False if you want blinking

# Blinking Windspeed Threshold
WIND_BLINK_THRESHOLD	= 15				# Knots of windspeed
ALWAYS_BLINK_FOR_GUSTS	= True				# Always animate for Gusts (regardless of speeds)

# Blinking Speed in seconds
BLINK_SPEED		= 1.0				# Float in seconds, e.g. 0.5 for half a second

# Total blinking time in seconds.
# For example set this to 300 to keep blinking for 5 minutes if you plan to run the script every 5 minutes to fetch the updated weather
BLINK_TOTALTIME_SECONDS	= 300

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
conditionDict = { "": {"flightCategory" : "", "windSpeed" : 0, "windGust" : False, "lightning": False } }
for metar in root.iter('METAR'):
	stationId = metar.find('station_id').text
	if metar.find('flight_category') is None:
		print("Missing flight condition, skipping.")
		continue
	flightCategory = metar.find('flight_category').text
	windGust = False
	if metar.find('wind_gust_kt') is None:
		windGust = False
	else:
		windGust = (True if (ALWAYS_BLINK_FOR_GUSTS or int(metar.find('wind_gust_kt').text) > WIND_BLINK_THRESHOLD) else False)
	if metar.find('wind_speed_kt') is None:
		print("Missing Wind speed, skipping.")
		continue
	windSpeed = metar.find('wind_speed_kt').text
	if metar.find('raw_text') is None:
		print("No Raw text found")
		continue
	rawText = metar.find('raw_text').text
	lightning = False if rawText.find('LTG') == -1 else True
	print(stationId + ":" + flightCategory + ":" + windSpeed + ":" + str(windGust) + ":" + str(lightning))
	conditionDict[stationId] = { "flightCategory" : flightCategory, "windSpeed" : int(windSpeed), "windGust": windGust, "lightning": lightning }

# Setting LED colors based on weather conditions
looplimit = int(round(BLINK_TOTALTIME_SECONDS / BLINK_SPEED)) if (ACTIVATE_WINDCONDITION_ANIMATION or ACTIVATE_LIGHTNING_ANIMATION) else 1
windCycle = False
while looplimit > 0:
	i = 0
	for airportcode in airports:
		# Skip NULL entries
		if airportcode == "NULL":
			i += 1
			continue

		color = COLOR_CLEAR
		conditions = conditionDict.get(airportcode, None)

		if conditions != None:
			windy = True if (ACTIVATE_WINDCONDITION_ANIMATION and windCycle == True and (conditions["windSpeed"] > WIND_BLINK_THRESHOLD or conditions["windGust"] == True)) else False
			lightningConditions = True if (ACTIVATE_LIGHTNING_ANIMATION and windCycle == False and conditions["lightning"] == True) else False
			if conditions["flightCategory"] == "VFR":
				color = COLOR_VFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_VFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			elif conditions["flightCategory"] == "MVFR":
				color = COLOR_MVFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_MVFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			elif conditions["flightCategory"] == "IFR":
				color = COLOR_IFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_IFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			elif conditions["flightCategory"] == "LIFR":
				color = COLOR_LIFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_LIFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			else:
				color = COLOR_CLEAR
		print("Setting LED " + str(i) + " for " + airportcode + " to " + ("lightning " if lightningConditions else "") + ("windy " if windy else "") + (conditions["flightCategory"] if conditions != None else "None") + " " + str(color))
		pixels[i] = color
		i += 1

	# Update actual LEDs all at once
	pixels.show()

	# Switching between animation cycles
	time.sleep(BLINK_SPEED)
	windCycle = False if windCycle else True
	looplimit -= 1

print()
print("Done")
