import board
import neopixel
try:
	import displaymetar
except ImportError:
	displaymetar = None

pixels = neopixel.NeoPixel(board.D18, 50)

pixels.deinit()

if displaymetar is not None:
	disp = displaymetar.startDisplay()
	displaymetar.shutdownDisplay(disp)

print("LEDs off")