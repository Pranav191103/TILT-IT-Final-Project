# oled_test.py – test SSD1306 OLED

import time
import board
import adafruit_ssd1306

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.show()

# Line 1: course title / game
oled.text("TECHIN 512", 10, 10, 1)
# Line 2: your game name
oled.text("TILT-IT", 30, 30, 1)
# Line 3: your name
oled.text("Pranav", 40, 46, 1)
oled.show()

while True:
    time.sleep(1)