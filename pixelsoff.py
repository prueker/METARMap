import board
import neopixel

pixels = neopixel.NeoPixel(board.D18, 50)

pixels.deinit()

print("LEDs off")
