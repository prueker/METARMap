#!/usr/bin/env python3.7

import os, sys
import urllib.request
import xml.etree.ElementTree as ET
import pprint

# Append module path for the example, since we're in a sub directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.forecast import generateForecast

# Read the airports file to retrieve list of airports and use as order for LEDs
# with open("/home/pi/airports") as f:
with open("./airports") as f:
    airports = f.readlines()
airports = [x.strip() for x in airports]

# Retrieve METAR from aviationweather.gov data server
# Details about parameters can be found here: https://www.aviationweather.gov/dataserver/example?datatype=taf
url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=tafs&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + ",".join([item for item in airports if item != "NULL"])
print(url)
print()

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'
})
content = urllib.request.urlopen(req).read()

# Retrieve flying conditions from the service response and store in a dictionary for each airport
root = ET.fromstring(content)
conditionDict = { "":"" }
for taf in root.iter('TAF'):
    stationId = taf.find('station_id').text
    forecast = generateForecast(taf, stationId)
    conditionDict[stationId] = forecast

print()
pprint.PrettyPrinter(indent = 2).pprint(conditionDict)
print()
print("Done")
