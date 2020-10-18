import board
import neopixel

NUMBER_OF_LEDS = 150
pixels = neopixel.NeoPixel(board.D18, NUMBER_OF_LEDS)

for index in range(len(pixels)):
    print(index)
    pixels[index] = (255, 255, 255)
    input("press enter to continue")
    pixels[index] = (0, 0, 0)
