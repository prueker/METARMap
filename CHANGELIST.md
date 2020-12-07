### 1.3.0 (2020-12-06)

**Major update**

Adding forecasting functionality with TAFs. To utilize, run the alternative `loop.py` script instead of `metar.py`. Requires additional hardware on the Raspberry Pi (see README).

No changes affect the existing `metar.py` script functionality
- New script, `loop.py`, that runs infinitely
- New lib, `lib/forecast.py` to compute flight category (+ more) by time based on TAF
- New lib, `lib/display.py` to update the lights and accompanying OLED screen (only used by `loop.py`)
- New example scripts in `examples` to help initial development. The metar and taf examples can be run outside of a Raspberry Pi environment

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
