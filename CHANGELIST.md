### LLH1.4.2 (2020-12-28)
- Added two cycles to each iaco. It will use half the DISPLAY_ROTATION_SPEED to cycle to the second screen.
- Updated some of the values, including local time along with Zulu

### 1.4.1 (2020-12-16)
- Small bugfix for CLR skycondition (which doesn't have a cloudbase)

### 1.4.0 (2020-12-15)
- Adding functionality to display METAR information for the airports in use on a small external display
- - Code is written for a 128 x 64 pixel external OLED display using the SSD1306 chipset

### 1.3.1 (2020-12-13)
- Astral for dimming using sunrise/sunset has a breaking change starting with python 3.6
- - Made a fix to support both older raspberry pi running python 3.5 with Astral 1.10.1 as well as newer Raspberry images running Astral 2.2

### 1.3.0 (2020-12-12)
- Adding functionality to dim the lights between certain times of day
  - Either as a fixed time of day
  - or using local sunrise/sunset times

### 1.2.3 (2020-11-19)
- Aviationweather.gov has stopped accepting the default user agent for urllib
- - Explicitly Setting it to standard web browser compatible user agent

### 1.2.2 (2020-06-11)
- Small fix to ensure correct variable scoping

### 1.2.1 (2020-05-21)
- Change to not skip station if wind is not currently reported, but the Flight condition is

### 1.2.0 (2020-05-18)
- Adding functionality to show lightning conditions in vicinity of the airport

### 1.1.2 (2020-05-12)
- Small fix to the loop condition

### 1.1.1 (2020-05-09)
- Small fix for IFR color duplicate value

### 1.1.0 (2020-05-08)
- Adding blinking functionality for windy conditions

### 1.0.1 (2020-04-19)
- Fixed LED_BRIGHTNESS not working

### 1.0 (2019-01-05)
- Initial version of the script
