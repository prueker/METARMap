import asyncio
from pytz import timezone
import busio
import board
import neopixel
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

TIME_ZONE = 'US/Eastern'

LED_PIN         = board.D18             # GPIO pin connected to the pixels (18 is PCM).
LED_COUNT       = 50                    # Number of LED pixels.
LED_BRIGHTNESS  = 0.3                   # Float from 0.0 (min) to 1.0 (max)

BLINK_RATE = 1
BLINK_WIND_THRESHOLD = 12
BLINK_GUST_THRESHOLD = 15

ANIMATE_BLINK_FOR_WIND = True
ANIMATE_BLINK_FOR_GUST = True
ANIMATE_BLINK_FOR_LIGHTNING = True

VFR = 'VFR'
MVFR = 'MVFR'
IFR = 'IFR'
LIFR = 'LIFR'

COLOR_VFR               = (255,0,0)             # Green
COLOR_MVFR              = (0,0,255)             # Blue
COLOR_IFR               = (0,255,0)             # Red
COLOR_LIFR              = (0,125,125)           # Magenta
COLOR_CLEAR             = (0,0,0)               # Clear

# Initialize the LED strip
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = LED_BRIGHTNESS, auto_write = False)

# Create the OLED display
i2c = busio.I2C(board.SCL, board.SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
width = disp.width
height = disp.height

# Create the image draw for OLED display
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

# Load font
font = ImageFont.truetype('font.tff', 24)

# Black box to clear OLED
def clear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(image)
clear()
disp.show()

def getColorForFlightCategory(flightCategory):
    if flightCategory == VFR:
        return COLOR_VFR
    if flightCategory == MVFR:
        return COLOR_MVFR
    if flightCategory == IFR:
        return COLOR_IFR
    if flightCategory == LIFR:
        return COLOR_LIFR
    return COLOR_CLEAR

def findForecastForTime(time, forecasts):
    forecastTime = time.replace(tzinfo=timezone(TIME_ZONE))
    for forecast in forecasts:
        start = forecast.get('startTime').replace(tzinfo=timezone('UTC')).astimezone(timezone('UTC'))
        end = forecast.get('endTime').replace(tzinfo=timezone('UTC')).astimezone(timezone('UTC'))
        if (start < forecastTime and forecastTime < end):
            return forecast
    return { "":"" }

blinkDict = { '':'' }

def blink(i, originalColor, isOff = None):
    color = COLOR_CLEAR if (isOff) else originalColor
    pixels[i] = color
    pixels.show()
    loop = asyncio.get_running_loop()
    blinkDict[i] =  loop.call_later(BLINK_RATE, blink, i, originalColor, not isOff)

def cancelBlink(i):
    if type(blinkDict.get(i)) is asyncio.TimerHandle:
        blinkDict.get(i).cancel()
        blinkDict[i] = None

def cancelAllBlinks():
    for i in list(blinkDict.keys()):
        cancelBlink(i)

def changeLightsBasedOnMetar(airports, metarDict):
    # TODO: IMPLEMENT AND TEST BLINKING FOR LIGHTNING (can't find a TAF with lightning yet)
    cancelAllBlinks()
    i = 0
    for airportcode in airports:
        if airportcode == "NULL":
            i += 1
            continue
        metar = metarDict.get(airportcode, 'No')
        if (metar == 'No'):
            pixels[i] = COLOR_CLEAR
            i += 1
            continue
        flightCategory = metar.get('flightCategory')
        windSpeed = metar.get('windSpeed', 0)
        windGust = metar.get('windGust', 0)
        lightning = metar.get('lightning', False)
        color = getColorForFlightCategory(flightCategory)
        pixels[i] = color
        shouldBlink = ((windSpeed > BLINK_WIND_THRESHOLD and ANIMATE_BLINK_FOR_WIND)
            or (windGust > BLINK_GUST_THRESHOLD and ANIMATE_BLINK_FOR_GUST))
        if (shouldBlink):
            blink(i, color)
        i += 1
    pixels.show()

def changeLightsBasedOnTaf(airports, forecastDict, forecastTime):
    # TODO: IMPLEMENT AND TEST BLINKING FOR LIGHTNING (can't find a TAF with lightning yet)
    cancelAllBlinks()
    i = 0
    for airportcode in airports:
        if airportcode == "NULL":
            i += 1
            continue
        forecasts = forecastDict.get(airportcode,"No")
        if forecasts == "No":
            pixels[i] = COLOR_CLEAR
            i += 1
            continue
        forecastPeriod = findForecastForTime(forecastTime, forecasts)
        forecast = forecastPeriod.get('forecast', {})
        flightCategory = forecastPeriod.get('flightCategory')
        windSpeed = forecast.get('windSpeed', 0)
        windGust = forecast.get('windGust', 0)
        lightning = forecast.get('lightning', False)
        color = getColorForFlightCategory(flightCategory)
        pixels[i] = color
        shouldBlink = ((windSpeed > BLINK_WIND_THRESHOLD and ANIMATE_BLINK_FOR_WIND)
            or (windGust > BLINK_GUST_THRESHOLD and ANIMATE_BLINK_FOR_GUST))
        if (shouldBlink):
            blink(i, color)
        i += 1
    pixels.show()

def changeDisplay(time):
    clear()
    draw.text((0, -4), time.strftime('%a %H:%M'), font=font, fill=255)
    disp.image(image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT))
    disp.show()
