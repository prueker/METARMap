import board
import neopixel


# Global Configuration Variables

# NeoPixel LED Configuration
LED_COUNT			= 150				# Number of LED pixels.
LED_PIN				= board.D18			# GPIO pin connected to the pixels (18 is PCM).
LED_BRIGHTNESS			= 0.5				# Float from 0.0 (min) to 1.0 (max)
LED_ORDER			= neopixel.GRB			# Strip type and colour ordering

COLOR_VFR		= (255,0,0)			# Green
COLOR_VFR_FADE		= (125,0,0)			# Green Fade for wind
COLOR_MVFR		= (0,0,255)			# Blue
COLOR_MVFR_FADE		= (0,0,125)			# Blue Fade for wind
COLOR_IFR		= (0,255,0)			# Red
COLOR_IFR_FADE		= (0,125,0)			# Red Fade for wind
COLOR_LIFR		= (0,125,125)			# Magenta
COLOR_LIFR_FADE		= (0,75,75)			# Magenta Fade for wind
COLOR_CLEAR		= (0,0,0)			# Clear
COLOR_LIGHTNING		= (255,255,255)			# White

# Do you want the METARMap to be static to just show flight conditions, or do you also want blinking/fading based on current wind conditions
ACTIVATE_WINDCONDITION_ANIMATION = False		# Set this to False for Static or True for animated wind conditions

#Do you want the Map to Flash white for lightning in the area
ACTIVATE_LIGHTNING_ANIMATION = False			# Set this to False for Static or True for animated Lightning

# Fade instead of blink
FADE_INSTEAD_OF_BLINK	= True				# Set to False if you want blinking

# Blinking Windspeed Threshold
WIND_BLINK_THRESHOLD	= 15				# Knots of windspeed
ALWAYS_BLINK_FOR_GUSTS	= False				# Always animate for Gusts (regardless of speeds)

# Blinking Speed in seconds
BLINK_SPEED		= 1.0				# Float in seconds, e.g. 0.5 for half a second

# Total blinking time in seconds.
# For example set this to 300 to keep blinking for 5 minutes if you plan to run the script every 5 minutes to fetch the updated weather
BLINK_TOTALTIME_SECONDS	= 300

