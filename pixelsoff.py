import board
import neopixel
import config

pixels = neopixel.NeoPixel(board.D18, config.LED_COUNT)

pixels.deinit()

print("LEDs off")
