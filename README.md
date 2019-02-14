# METARMap
Raspberry Pi project to visualize flight conditions on a map using WS8211 LEDs addressed via NeoPixel

## Detailed instructions
I've created detailed instructions about the setup and parts used here: https://slingtsi.rueker.com/making-a-led-powered-metar-map-for-your-wall/

## Software Setup
* Install [Raspbian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/) on SD card
* [Enable Wi-Fi and SSH](https://medium.com/@danidudas/install-raspbian-jessie-lite-and-setup-wi-fi-without-access-to-command-line-or-using-the-network-97f065af722e)
* Install SD card and power up Raspberry Pi
* SSH (using [Putty](https://www.putty.org) or some other SSH tool) into the Raspberry and configure password and timezones
	* passwd
	* sudo raspi-config
* Update packages 
	* sudo apt-get update
	* sudo apt-get upgrade
* Copy the **metar.py**, **airports**, **startup.sh**, **refresh.sh** scripts into the pi home directory
* Install python3 and pip3 if not already installed
	* sudo apt-get install python3
	* sudo apt-get install python3-pip
* Install required python libraries for the project
	* [Neopixel](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage): sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
* Attach WS8211 LEDs to Raspberry Pi, if you are using just a few, you can connect the directly, otherwise you may need to also attach external power to the LEDs. For my purpose with 22 powered LEDs it was fine to just connect it directly. You can find [more details about wiring here](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring).
* Test the script by running it directly (it needs to run with root permissions to access the GPIO pins):
	* sudo python3 metar.py
* Make appropriate changes to the **airports** file for the airports you want to use and change the **metar.py** script to the correct **LED_COUNT** (including NULLs if you have LEDS in between airports that will stay off) and **LED_BRIGHTNESS** if you want to change it
* To run the script automatically when you power the Raspberry Pi, you will need to grant permissions to execute the **startup.sh** script and read permissions to the **airports** and **metar.py** script using chmod
* Change the **/etc/rc.local** file to automatically run the **startup.sh** script, you can refer to the rc.local file in Github for reference
* Try it out by disconnecting your Raspberry Pi from the power and reconnecting it and waiting a couple seconds
* You can check the **/home/pi/startup.log** file to see if any errors occurred
* If you'd like to have the script refresh in regular intervals, use crontab and set the appropriate interval. For an example you can refer to the crontab file in the GitHub repo, which runs the script once every 5 minutes (make sure you grant the file execute permissions beforehand). To edit your crontab type:
	* crontab -e
