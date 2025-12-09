# code.py – Tilt-It final game
#
# Main game logic for TECHIN 512 Final Project
#
# Hardware:
# - Seeed XIAO ESP32C3
# - SSD1306 128x64 OLED (I2C)
# - ADXL345 accelerometer (I2C)
# - Rotary encoder (A/B + push button)
# - Single NeoPixel LED
# - LiPo battery + switch (power only, not read in code)

import time
import random
import board
import neopixel
from digitalio import DigitalInOut, Direction, Pull
import adafruit_ssd1306
import adafruit_adxl34x

#
# -----------------------
#   HARDWARE SETUP
# -----------------------
#

# ---- I2C devices: OLED + ADXL345 ----
i2c = board.I2C()  # uses board.SCL, board.SDA
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
accel = adafruit_adxl34x.ADXL345(i2c)

# ---- NeoPixel (1 LED) ----
# Change D7 if you wired to a different pin
PIXEL_PIN = board.D7
pixels = neopixel.NeoPixel(PIXEL_PIN, 1, brightness=0.3, auto_write=True)

# ---- Rotary encoder pins ----
# UPDATE these if your wiring is different.
encoder_a = DigitalInOut(board.D1)  # encoder A / CLK
encoder_a.direction = Direction.INPUT
encoder_a.pull = Pull.UP

encoder_b = DigitalInOut(board.D0)  # encoder B / DT
encoder_b.direction = Direction.INPUT
encoder_b.pull = Pull.UP

encoder_btn = DigitalInOut(board.D2)  # encoder push button
encoder_btn.direction = Direction.INPUT
encoder_btn.pull = Pull.UP


#
# -----------------------
#   SIMPLE ENCODER CLASS
# -----------------------
#

class SimpleEncoder:
    """
    Very simple quadrature decoder for a rotary encoder.
    Tracks relative position and direction.
    """
    def __init__(self, pin_a, pin_b):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.last_state = (self.pin_a.value, self.pin_b.value)
        self.position = 0

    def update(self):
        """
        Call frequently in the main loop.
        Returns:
            +1 if turned one 'step' in one direction,
            -1 if turned the other way,
             0 if no change.
        """
        state = (self.pin_a.value, self.pin_b.value)
        if state == self.last_state:
            return 0

        a_last, b_last = self.last_state
        a_now, b_now = state

        # Basic gray-code decoding
        delta = 0
        if a_last == a_now:
            # B changed
            if b_now != b_last:
                delta = 1 if a_now != b_now else -1
        elif b_last == b_now:
            # A changed
            if a_now != a_last:
                delta = 1 if a_now == b_now else -1

        self.position += delta
        self.last_state = state
        return delta


encoder = SimpleEncoder(encoder_a, encoder_b)


#
# -----------------------
#   GAME CONFIG
# -----------------------
#

MOVES = ["SHAKE", "LEFT", "RIGHT", "BUTTON"]

DIFFICULTIES = [
    {"name": "EASY",   "base_time": 4.0},
    {"name": "MEDIUM", "base_time": 3.0},
    {"name": "HARD",   "base_time": 2.0},
]

MAX_LEVEL = 10

# Simple accelerometer "calibration":
# We'll treat anything below this G-force as "rest".
SHAKE_THRESHOLD = 13.0  # m/s^2-ish; adjust after testing


#
# -----------------------
#   OLED HELPERS
# -----------------------
#

def clear_oled():
    oled.fill(0)
    oled.show()


def center_text(text, y=None):
    """
    Draw single line of text horizontally centered.
    If y is None, put approximately in vertical center.
    """
    clear_oled()
    # 6px wide per char (default font), 8px tall
    width = len(text) * 6
    x = max(0, (128 - width) // 2)
    if y is None:
        y = (64 - 8) // 2
    oled.text(text, x, y, 1)
    oled.show()


def show_two_lines(line1, line2):
    clear_oled()
    # line1 near top, line2 near center
    oled.text(line1, 0, 10, 1)
    oled.text(line2, 0, 32, 1)
    oled.show()


#
# -----------------------
#   INPUT HELPERS
# -----------------------
#

def wait_for_button_press(timeout=None):
    """
    Wait for encoder button press.
    If timeout is None -> wait forever.
    If timeout is set -> return True if pressed, False if expired.
    """
    start = time.monotonic()
    while True:
        if not encoder_btn.value:  # active LOW
            # wait for release
            while not encoder_btn.value:
                time.sleep(0.02)
            return True
        if timeout is not None and (time.monotonic() - start) > timeout:
            return False
        time.sleep(0.02)


def get_shake_detected():
    """
    Return True if the accelerometer detects a "shake".
    """
    x, y, z = accel.acceleration
    # Simple magnitude estimate
    mag = abs(x) + abs(y) + abs(z)
    return mag > SHAKE_THRESHOLD


def wait_for_move(expected_move, time_limit):
    """
    Wait for the player to perform the expected move
    within the given time limit (seconds).
    Returns True on success, False on timeout / wrong move.
    """
    start = time.monotonic()
    last_pos = encoder.position

    while (time.monotonic() - start) < time_limit:
        # Update encoder
        delta = encoder.update()

        # Check each move type
        if expected_move == "SHAKE":
            if get_shake_detected():
                return True

        elif expected_move == "BUTTON":
            if not encoder_btn.value:
                # debounce
                while not encoder_btn.value:
                    time.sleep(0.02)
                return True

        elif expected_move == "LEFT":
            if delta < 0:
                return True

        elif expected_move == "RIGHT":
            if delta > 0:
                return True

        time.sleep(0.01)

    return False


#
# -----------------------
#   GAME SCREENS
# -----------------------
#

def splash_screen():
    pixels[0] = (0, 0, 50)  # dim blue
    pixels.show()
    center_text("TILT-IT")
    time.sleep(1.5)

    clear_oled()
    oled.text("TILT-IT", 30, 10, 1)
    oled.text("Press button", 10, 30, 1)
    oled.text("to start", 25, 42, 1)
    oled.show()

    wait_for_button_press()


def choose_difficulty():
    """
    Rotate encoder to choose difficulty, press button to confirm.
    Returns difficulty dict.
    """
    index = 0
    last_pos = encoder.position
    pixels[0] = (0, 0, 100)  # blue

    while True:
        delta = encoder.update()
        if delta != 0:
            index = (index + delta) % len(DIFFICULTIES)

        diff = DIFFICULTIES[index]
        clear_oled()
        oled.text("Select Difficulty:", 0, 10, 1)
        center_text(diff["name"], y=30)
        oled.text("Press to confirm", 5, 50, 1)
        oled.show()

        if not encoder_btn.value:
            while not encoder_btn.value:
                time.sleep(0.02)
            pixels[0] = (0, 50, 0)  # green flash
            time.sleep(0.2)
            return diff

        time.sleep(0.05)


def show_level_and_move(level, move_name):
    clear_oled()
    oled.text("Level {}".format(level), 0, 0, 1)
    oled.text("Do this move:", 0, 16, 1)
    center_text(move_name, y=32)
    oled.show()


def show_game_over(level):
    pixels[0] = (255, 0, 0)  # red
    clear_oled()
    center_text("GAME OVER")
    oled.text("Reached level {}".format(level), 0, 40, 1)
    oled.show()
    time.sleep(2)

    clear_oled()
    oled.text("Press button", 10, 24, 1)
    oled.text("to restart", 18, 36, 1)
    oled.show()
    wait_for_button_press()
    pixels[0] = (0, 0, 0)


def show_game_win():
    # show some "celebration"
    for _ in range(3):
        pixels[0] = (0, 255, 0)  # green
        time.sleep(0.2)
        pixels[0] = (0, 0, 255)  # blue
        time.sleep(0.2)
        pixels[0] = (255, 255, 0)  # yellow
        time.sleep(0.2)
    pixels[0] = (0, 0, 0)

    clear_oled()
    center_text("YOU WIN!")
    oled.text("Congrats!", 30, 40, 1)
    oled.show()
    time.sleep(2)

    clear_oled()
    oled.text("Press button", 10, 24, 1)
    oled.text("to play again", 12, 36, 1)
    oled.show()
    wait_for_button_press()


#
# -----------------------
#   MAIN GAME LOOP
# -----------------------
#

def play_game():
    while True:
        splash_screen()
        difficulty = choose_difficulty()
        base_time = difficulty["base_time"]

        level = 1

        while True:
            pixels[0] = (0, 10, 0)  # dim green during level
            # Choose move
            current_move = random.choice(MOVES)

            # Display level & move
            show_level_and_move(level, current_move)

            # Time limit gets slightly shorter each level
            time_limit = max(1.0, base_time - (level - 1) * 0.2)

            success = wait_for_move(current_move, time_limit)

            if success:
                # Flash green
                pixels[0] = (0, 255, 0)
                time.sleep(0.2)
                pixels[0] = (0, 0, 0)
                level += 1

                if level > MAX_LEVEL:
                    show_game_win()
                    break  # break out of inner loop and restart game

            else:
                show_game_over(level)
                break  # restart whole game (outer while)

        # loop restarts: splash_screen -> choose_difficulty -> game


# --- Entry point ---
clear_oled()
pixels[0] = (0, 0, 0)
play_game()