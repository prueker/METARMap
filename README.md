# METARMap
Raspberry Pi project to visualize flight conditions on a map using WS8211 LEDs addressed via NeoPixel

## Detailed instructions
I've created detailed instructions about the setup and parts used here: https://slingtsi.rueker.com/making-a-led-powered-metar-map-for-your-wall/

## Software Setup
* Install [Raspbian Buster Lite](https://www.raspberrypi.org/downloads/raspbian/) on SD card
* [Enable Wi-Fi and SSH](https://medium.com/@danidudas/install-raspbian-jessie-lite-and-setup-wi-fi-without-access-to-command-line-or-using-the-network-97f065af722e)
* Install SD card and power up Raspberry Pi
* SSH (using [Putty](https://www.putty.org) or some other SSH tool) into the Raspberry and configure password and timezones
	* `passwd`
	* `sudo raspi-config`
* Update packages 
	* `sudo apt-get update`
	* `sudo apt-get upgrade`
* Copy the **metar.py**, **pixelsoff.py**, **airports**, **refresh.sh** and **lightsoff.sh** scripts into the pi home directory (/home/pi)
* Install python3 and pip3 if not already installed
	* `sudo apt-get install python3`
	* `sudo apt-get install python3-pip`
* Install required python libraries for the project
	* [Neopixel](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage): `sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel`
* Attach WS8211 LEDs to Raspberry Pi, if you are using just a few, you can connect the directly, otherwise you may need to also attach external power to the LEDs. For my purpose with 22 powered LEDs it was fine to just connect it directly. You can find [more details about wiring here](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring).
* Test the script by running it directly (it needs to run with root permissions to access the GPIO pins):
	* `sudo python3 metar.py`
* Make appropriate changes to the **airports** file for the airports you want to use and change the **metar.py** and **pixelsoff.py** script to the correct **LED_COUNT** (including NULLs if you have LEDS in between airports that will stay off) and **LED_BRIGHTNESS** if you want to change it
* To run the script automatically when you power the Raspberry Pi, you will need to grant permissions to execute the **refresh.sh** and **lightsoff.sh** script and read permissions to the **airports**, **metar.py** and **pixelsoff.py** script using chmod:
	* `chmod +x filename` will grant execute permissions
	* `chmod +r filename` will grant write permissions
* To have the script start up automatically and refresh in regular intervals, use crontab and set the appropriate interval. For an example you can refer to the crontab file in the GitHub repo (make sure you grant the file execute permissions beforehand to the refresh.sh and lightsoff.sh file). To edit your crontab type: **`crontab -e`**, after you are done with the edits, exit out by pressing **ctrl+x** and confirm the write operation
	* The sample crontab will run the script every 5 minutes (the */5) between the hours of 7 to 21, which includes the 21 hour, so it means it will run until 21:55
	* Then at 22:05 it will run the lightsoff.sh script, which will turn all the lights off

### Using `find_airports.py`

`find_airports.py` is provided as a utility to associate LEDs with airports. Run `sudo python3 find_airports.py` to light up each LED one at a time. You can then write down the illuminated airport in your version of the `airports` file.

## Additional Wind condition blinking/fading functionality
I recently expanded the script to also take wind condition into account and if the wind exceeds a certain threshold, or if it is gusting, make the LED for that airport either blink on/off or to fade between  two shades of the current flight category color.

If you want to use this extra functionality, then inside the **metar.py** file set the **ACTIVATE_WINDCONDITION_ANIMATION** parameter to **True**.
* There are a few additional parameters in the script you can configure to your liking:
	* FADE_INSTEAD_OF_BLINK - set this to either **True** or **False** to switch between fading or blinking for the LEDs when conditions are windy
	* WIND_BLINK_THRESHOLD - in Knots for normal wind speeds currently at the airport
	* ALWAYS_BLINK_FOR_GUSTS - If you always want the blinking/fading to happen for gusts, regardless of the wind speed
	* BLINKS_SPEED - How fast the blinking happens, I found 1 second to be a happy medium so it's not too busy, but you can also make it faster, for example every half a second by using 0.5
	* BLINK_TOTALTIME_SECONDS = How long do you want the script to run. I have this set to 300 seconds as I have my crontab setup to re-run the script every 5 minutes to get the latest weather information
	
## Additional Lightning in the vicinity blinking functionality
After the recent addition for wind condition animation, I got another request from someone if I could add a white blinking animation to represent lightning in the area.
Please note that due to the nature of the METAR system, this means that the METAR for this airport reports that there is Lightning somewhere in the vicinity of the airport, but not necessarily right at the airport.

If you want to use this extra functionality, then inside the **metar.py** file set the **ACTIVATE_LIGHTNING_ANIMATION** parameter to **True**.
* This shares two configuration parameters together with the wind animation that you can modify as you like:
	* BLINKS_SPEED - How fast the blinking happens, I found 1 second to be a happy medium so it's not too busy, but you can also make it faster, for example every half a second by using 0.5
	* BLINK_TOTALTIME_SECONDS = How long do you want the script to run. I have this set to 300 seconds as I have my crontab setup to re-run the script every 5 minutes to get the latest weather information
