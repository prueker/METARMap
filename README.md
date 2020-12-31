# METARMap (with TAF)

## What's different about this than the parent repo?
This file contains instructions for setting up the METARMap with TAF functionality. Unfortunately, due to technical details I won't get into here, I could not add the functionality on top of the existing parent repo's scripts, so I had to write some new ones. I ended up deleting all of the parent repo's scripts in favor of my own, to prevent confusion due to multiple entry points.

It also requires some extra hardware on the Raspberry Pi, because you need a way to adjust the time for which the lights are forecasting. I came up with the following approach:
1. A "potentiometer" is hooked up to the Pi (through an Analog-to-Digital Converter)
1. An OLED screen is hooked up to the Pi
1. The lights are hooked up to the Pi in the same manner as the regular METARMap.
1. A script runs an infinitely running asynchronous event loop
1. Recursive functions schedule themselves on the event loop after a delay period. By default, the data fetching schedules every 5 minutes while the potentiometer listener schedules every 0.2 seconds.
1. If the potentiometer listener detects a change, it schedules an update to the OLED screen and lights

## Changelist
To see a list of changes to the scripts over time, refer to [CHANGELIST.md](CHANGELIST.md)

## Detailed instructions
The owner of the parent repo created detailed instructions about the setup and parts used here: https://slingtsi.rueker.com/making-a-led-powered-metar-map-for-your-wall/. However they are for the regular METARMap, and there are several additional steps for this version not included in those instructions.

## Software Setup
* Install [Raspbian Buster Lite](https://www.raspberrypi.org/downloads/raspbian/) on SD card
  * You can also use the [Raspberry Pi Imager](https://www.raspberrypi.org/software/) which downloads and burns the image for you
* [Enable Wi-Fi and SSH](https://medium.com/@danidudas/install-raspbian-jessie-lite-and-setup-wi-fi-without-access-to-command-line-or-using-the-network-97f065af722e)
* Install SD card and power up Raspberry Pi
* SSH (using [Putty](https://www.putty.org) or some other SSH tool) into the Raspberry and configure password and timezones
	* `passwd`
	* `sudo raspi-config`
* Update packages
	* `sudo apt-get update`
	* `sudo apt-get upgrade`
* Install python3 and pip3 if not already installed
	* `sudo apt-get install python3`
	* `sudo apt-get install python3-pip`
* **Ensure** python 3.7 or greater was installed
  * `sudo python3 --version`
* Install required python libraries for the project
	* [Neopixel](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage): `sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel`
  * [Analog-to-Digital Converter](https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/ads1015-slash-ads1115):
    * `sudo apt-get install build-essential python-dev python-smbus`
    * `sudo pip3 install adafruit-ads1x15`
  * [OLED Screen](https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage):
    * `sudo pip3 install adafruit-circuitpython-ssd1306`
    * `sudo apt-get install python3-pil` (use apt-git b/c this also install other dependencies)
* [Enable I2C](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c) on the Raspberry Pi. I2C is a communication protocol that allows multiple devices to communicate. All devices attach to the same I2C pins (SDA and SCL).
* Attach WS8211 LEDs to Raspberry Pi
  * If you've read the README.md for the regular METARMap, you may remember the instructions say you can power the strip of the Pi alone. I don't recommend that for this project given that the Pi will be powering 3 other devices on its 3v supply. I know very little about the allowed current draw on the Pi, but to be safe I used an external 5V (10A) power supply which powers both the Pi and the lights. You can find [more details about wiring here](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring).
  * Connect to 5V external power, ground, and GPIO (18 by default)
* Attach Analog-to-Digital Converter (ADC)
  * Connect to Pi 3.3V and ground
  * Connect SCL to Pi SCL and SDA to Pi SDA. These are for the Pi I2C
* Attach potentiometer to ADC and Raspberry Pi (I used a 3.3V sliding potentiometer). There should be 3 pins. The potentiometer is analog, which is why it must go through the ADC before it reaches the Pi.
  * Connect to Pi 3.3V and ground
  * Connect the data line (whatever it's called on your potentiometer) to the ADC A0 pin
* Attach OLED screen to Raspberry Pi
  * Connect to Pi 3.3V and ground
  * Connect SCL to Pi SCL and SDA to Pi SDA. These are for the Pi I2C
* Test the devices separately by running the example scripts:
  * `sudo python3 examples/screen.py`
  * `sudo python3 examples/slider.py`
  * **!!IF YOUR POTENTIOMETER!!** is not 3.3V, adjust the SLIDER_MAX_VOLTAGE in the `loop.py` script
* Test the API fetches by running the example scripts:
  * `sudo python3 examples/metar.py`
  * `sudo python3 examples/taf.py`
* Test the script by running it directly (it needs to run with root permissions to access the GPIO pins):
	* `sudo python3 loop.py` (`CTRL+C` to cancel)
* Make appropriate changes to the **airports** file for the airports you want to use and verify the `lib/display.py` file has the correct number of LEDs in **LED_COUNT** (it must be at least the number of LEDs on your strip) and change **LED_BRIGHTNESS** if you so desire
* When you run `loop.py`, it runs infinitely until you press `CTRL+C`. Adjust the potentiometer and the screen should update with the forecasting time. The lights should adjust based on the weather conditions
* You can write an `on.sh` and `off.sh` to start and stop the python `loop.py` script. Then you can use `crontab` to run them automatically at whatever time. See `crontab` docs.

* **THERE IS NOT CURRENTLY A WAY** to run the script on startup (should be easy to figure out, but still developing)

## Additional Wind condition blinking/fading functionality
The script also takes wind condition into account and if the wind exceeds a certain threshold, or if it is gusting, the LED for that airport will either blink on/off or fade between two shades of the current flight category color.

#### Not all of the blinking/fading functionality from the parent repo has been ported over to this TAF version yet
- [ ] Fading instead of blinking
- [ ] Always blink for gusts

If you do not want to use this extra functionality, then inside the **lib/display.py** file set the **ANIMATE_BLINK_FOR_WIND** parameter to **False**, and similarly for gusts and lightning. There are a few additional parameters in the script you can configure to your liking:
  * ANIMATE_BLINK_FOR_WIND - If you want the blinking/fading to happen for high wind
  * ANIMATE_BLINK_FOR_GUST - If you want the blinking/fading to happen for high gusts
  * ~~ANIMATE_BLINK_FOR_LIGHTNING - If you want the flashing to happen for lightning~~
  * ~~ALWAYS_BLINK_FOR_GUSTS - If you always want the blinking/fading to happen for gusts, regardless of the wind speed~~
	* ~~FADE_INSTEAD_OF_BLINK - set this to either **True** or **False** to switch between fading or blinking for the LEDs when conditions are windy~~
	* BLINK_WIND_THRESHOLD - in Knots, controls how fast wind needs to be in order to blink
  * BLINK_GUST_THRESHOLD - in Knots, controls how fast gusts need to be in order to blink
	* BLINK_RATE - How fast the blinking happens, I found 1 second to be a happy medium so it's not too busy, but you can also make it faster, for example every half a second by using 0.5

## Additional Lightning in the vicinity blinking functionality
After the recent addition for wind condition animation, the author of the parent repo got another request from someone to add a white blinking animation to represent lightning in the area.
Please note that due to the nature of the METAR system, this means that the METAR for this airport reports that there is Lightning somewhere in the vicinity of the airport, but not necessarily right at the airport.

If you do not want to use this extra functionality, then inside the **lib/display.py** file set the **ANIMATE_BLINK_FOR_LIGHTNING** parameter to **False**.
* This shares two configuration parameters together with the wind animation that you can modify as you like:
	* BLINKS_SPEED - How fast the blinking happens, I found 1 second to be a happy medium so it's not too busy, but you can also make it faster, for example every half a second by using 0.5
