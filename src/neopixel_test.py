# neopixel_test.py – test single NeoPixel
import time
import board
import neopixel

PIXEL_PIN = board.D7   # change if wired differently
pixels = neopixel.NeoPixel(PIXEL_PIN, 1, brightness=0.3, auto_write=True)

colors = [
    (255,   0,   0),  # red
    (0,   255,   0),  # green
    (0,     0, 255),  # blue
    (255, 255,   0),  # yellow
    (255,   0, 255),  # magenta
    (0,   255, 255),  # cyan
    (0,     0,   0),  # off
]

while True:
    for c in colors:
        pixels[0] = c
        time.sleep(0.4)