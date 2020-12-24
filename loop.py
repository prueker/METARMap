#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET
import datetime
import math
import logging
import asyncio
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from logging.handlers import RotatingFileHandler

from lib.forecast import generateForecast
from lib.display import changeDisplay, changeLightsBasedOnMetar, changeLightsBasedOnTaf

logDateFormat = '%m/%d %H:%M:%S'
logFormatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=logDateFormat)

logHandler = RotatingFileHandler('metar-map.log', maxBytes=5*1024*1024, backupCount=1, delay=0)
logHandler.setFormatter(logFormatter)
logHandler.setLevel(logging.INFO)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)


i2c = busio.I2C(board.SCL, board.SDA)   # Create the I2C bus
ads = ADS.ADS1115(i2c)                  # Create the ADC object using the I2C bus
chan = AnalogIn(ads, ADS.P0)            # Create single-ended input on channel 0

with open("/home/pi/METARMap/airports") as f:
    airports = f.readlines()
airports = [x.strip() for x in airports]

SLIDER_MAX_VOLTAGE = 3.32
SLIDER_STEP = SLIDER_MAX_VOLTAGE / 24
# https://www.aviationweather.gov/dataserver/example?datatype=metar
METAR_URL = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + ",".join([item for item in airports if item != "NULL"])
# https://www.aviationweather.gov/dataserver/example?datatype=taf
FORECAST_URL = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=tafs&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString="+ ",".join([item for item in airports if item != "NULL"])
REFRESH_RATE_FETCH = 300
REFRESH_RATE_SLIDER = 0.25

def getViewingTime():
    return min(math.floor(chan.voltage / SLIDER_STEP), 23)

loop = asyncio.get_event_loop()
currentViewingTimeDelta = getViewingTime()

################## Fetching METAR and TAFs ##################
metarDict = { "":"" }
forecastDict = { "":"" }

def populateMetars():
    logger.info('Fetching METARs')
    req = urllib.request.Request(METAR_URL, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'
    })
    content = urllib.request.urlopen(req).read()
    root = ET.fromstring(content)
    for metar in root.iter('METAR'):
        stationId = metar.find('station_id').text
        if metar.find('flight_category') is None:
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
        metarDict[stationId] = {
            'flightCategory': flightCategory,
            'windSpeed': windSpeed,
            'windGust': windGust,
            'lightning': lightning
        }

def populateForecasts():
    logger.info('Fetching TAFs')
    req = urllib.request.Request(FORECAST_URL, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'
    })
    content = urllib.request.urlopen(req).read()
    root = ET.fromstring(content)
    for taf in root.iter('TAF'):
        stationId = taf.find('station_id').text
        forecast = generateForecast(taf, stationId)
        forecastDict[stationId] = forecast

################ Changing lights / displays #################
def changeLights():
    global currentViewingTimeDelta
    forecastTime = datetime.datetime.now() + datetime.timedelta(hours=currentViewingTimeDelta)
    changeDisplay(forecastTime)
    if (currentViewingTimeDelta == 0):
        logger.info('Setting lights for observation: %s', forecastTime.strftime(logDateFormat))
        changeLightsBasedOnMetar(airports, metarDict)
    else:
        logger.info('Setting lights for forecast: %s', forecastTime.strftime(logDateFormat))
        changeLightsBasedOnTaf(airports, forecastDict, forecastTime)

################### Scheduling functions ####################
def checkIfChanged():
    global currentViewingTimeDelta
    viewingTimeDelta = getViewingTime()
    changed = viewingTimeDelta != currentViewingTimeDelta
    if (changed):
        logger.info('Detected slider step change:\n\t(Volt: %4.3f, Value: %d, OldDelta: %d, NewDelta: %d)',
            chan.voltage, chan.value, currentViewingTimeDelta, viewingTimeDelta
        )
        currentViewingTimeDelta = viewingTimeDelta
        loop.call_soon(changeLights)
    loop.call_later(REFRESH_RATE_SLIDER, checkIfChanged)

def populateMetarsAndForecasts():
    populateMetars()
    populateForecasts()
    loop.call_soon(changeLights)
    loop.call_later(REFRESH_RATE_FETCH, populateMetarsAndForecasts)

loop.call_soon(populateMetarsAndForecasts)
loop.call_soon(checkIfChanged)
loop.run_forever()
