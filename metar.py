#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET
import board
import neopixel
import time
import config

# Initialize the LED strip
pixels = neopixel.NeoPixel(
    config.LED_PIN, config.LED_COUNT, brightness=config.LED_BRIGHTNESS, pixel_order=config.LED_ORDER, auto_write=False)

# Read the airports file to retrieve list of airports and use as order for LEDs
with open("/home/pi/airports") as f:
    airports = f.readlines()
airports = [x.strip() for x in airports]

# Retrieve METAR from aviationweather.gov data server
# Details about parameters can be found here: https://www.aviationweather.gov/dataserver/example?datatype=metar
url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + \
    ",".join([item for item in airports if item != "NULL"])
print(url)

content = urllib.request.urlopen(url).read()

# Retrieve flying conditions from the service response and store in a dictionary for each airport
root = ET.fromstring(content)
conditionDict = {"": {"flightCategory": "",
                      "windSpeed": 0, "windGust": False, "lightning": False}}
for metar in root.iter('METAR'):
    stationId = metar.find('station_id').text
    if metar.find('flight_category') is None:
        print("Missing flight condition, skipping.")
        continue
    flightCategory = metar.find('flight_category').text
    windGust = False
    windSpeed = 0
    lightning = False
    if metar.find('wind_gust_kt') is not None:
        windGust = (True if (config.ALWAYS_BLINK_FOR_GUSTS or int(
            metar.find('wind_gust_kt').text) > config.WIND_BLINK_THRESHOLD) else False)
    if metar.find('wind_speed_kt') is not None:
        windSpeed = int(metar.find('wind_speed_kt').text)
    if metar.find('raw_text') is not None:
        rawText = metar.find('raw_text').text
        lightning = False if rawText.find('LTG') == -1 else True
    print(stationId + ":" + flightCategory + ":" + str(windSpeed) +
          ":" + str(windGust) + ":" + str(lightning))
    conditionDict[stationId] = {"flightCategory": flightCategory,
                                "windSpeed": windSpeed, "windGust": windGust, "lightning": lightning}

# Setting LED colors based on weather conditions
looplimit = int(round(config.BLINK_TOTALTIME_SECONDS / config.BLINK_SPEED)) if (
    config.ACTIVATE_WINDCONDITION_ANIMATION or config.ACTIVATE_LIGHTNING_ANIMATION) else 1
windCycle = False
while looplimit > 0:
    i = 0
    for airportcode in airports:
        # Skip NULL entries
        if airportcode == "NULL":
            i += 1
            continue

        color = config.COLOR_CLEAR
        conditions = conditionDict.get(airportcode, None)
        windy = False
        lightningConditions = False

        if conditions != None:
            windy = True if (config.ACTIVATE_WINDCONDITION_ANIMATION and windCycle == True and (
                conditions["windSpeed"] > config.WIND_BLINK_THRESHOLD or conditions["windGust"] == True)) else False
            lightningConditions = True if (
                config.ACTIVATE_LIGHTNING_ANIMATION and windCycle == False and conditions["lightning"] == True) else False
            if conditions["flightCategory"] == "VFR":
                color = config.COLOR_VFR if not (windy or lightningConditions) else config.COLOR_LIGHTNING if lightningConditions else (
                    config.COLOR_VFR_FADE if config.FADE_INSTEAD_OF_BLINK else config.COLOR_CLEAR) if windy else config.COLOR_CLEAR
            elif conditions["flightCategory"] == "MVFR":
                color = config.COLOR_MVFR if not (windy or lightningConditions) else config.COLOR_LIGHTNING if lightningConditions else (
                    config.COLOR_MVFR_FADE if config.FADE_INSTEAD_OF_BLINK else config.COLOR_CLEAR) if windy else config.COLOR_CLEAR
            elif conditions["flightCategory"] == "IFR":
                color = config.COLOR_IFR if not (windy or lightningConditions) else config.COLOR_LIGHTNING if lightningConditions else (
                    config.COLOR_IFR_FADE if config.FADE_INSTEAD_OF_BLINK else config.COLOR_CLEAR) if windy else config.COLOR_CLEAR
            elif conditions["flightCategory"] == "LIFR":
                color = config.COLOR_LIFR if not (windy or lightningConditions) else config.COLOR_LIGHTNING if lightningConditions else (
                    config.COLOR_LIFR_FADE if config.FADE_INSTEAD_OF_BLINK else config.COLOR_CLEAR) if windy else config.COLOR_CLEAR
            else:
                color = config.COLOR_CLEAR

        print("Setting LED " + str(i) + " for " + airportcode + " to " + ("lightning " if lightningConditions else "") +
              ("windy " if windy else "") + (conditions["flightCategory"] if conditions != None else "None") + " " + str(color))
        pixels[i] = color
        i += 1

    # Update actual LEDs all at once
    pixels.show()

    # Switching between animation cycles
    time.sleep(config.BLINK_SPEED)
    windCycle = False if windCycle else True
    looplimit -= 1

print()
print("Done")
