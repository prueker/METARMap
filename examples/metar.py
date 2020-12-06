#!/usr/bin/env python3.7

import urllib.request
import xml.etree.ElementTree as ET
import pprint

# Read the airports file to retrieve list of airports and use as order for LEDs
# with open("/home/pi/airports") as f:
with open("./airports") as f:
	airports = f.readlines()
airports = [x.strip() for x in airports]

# Retrieve METAR from aviationweather.gov data server
# Details about parameters can be found here: https://www.aviationweather.gov/dataserver/example?datatype=metar
url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + ",".join([item for item in airports if item != "NULL"])
print(url)
print()

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'
})
content = urllib.request.urlopen(req).read()

# Retrieve flying conditions from the service response and store in a dictionary for each airport
root = ET.fromstring(content)
conditionDict = { "":"" }
for metar in root.iter('METAR'):
	stationId = metar.find('station_id').text
	if metar.find('flight_category') is None:
		print('Missing flight condition for ' + stationId + ', skipping')
		continue
	flightCategory = metar.find('flight_category').text
	windSpeed = 0
	windGust = 0
	lightning = False
	if metar.find('wind_speed_kt') is not None:
		windSpeed = int(metar.find('wind_speed_kt').text)
	if metar.find('wind_gust_kt') is not None:
		windGust = int(metar.find('wind_gust_kt').text)
	if metar.find('raw_text') is not None:
		rawText = metar.find('raw_text').text
		lightning = False if rawText.find('LTG') == -1 else True
	conditionDict[stationId] = {
		'flightCategory': flightCategory,
		'windSpeed': windSpeed,
		'windGust': windGust,
		'lightning': lightning
	}

print()
pprint.PrettyPrinter(indent = 2).pprint(conditionDict)
print()
print("Done")
