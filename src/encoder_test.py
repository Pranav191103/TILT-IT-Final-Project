# encoder_test.py – test rotary encoder & button
import time
import board
from digitalio import DigitalInOut, Direction, Pull

# Pins – update if your wiring is different
encoder_a = DigitalInOut(board.D1)
encoder_a.direction = Direction.INPUT
encoder_a.pull = Pull.UP

encoder_b = DigitalInOut(board.D0)
encoder_b.direction = Direction.INPUT
encoder_b.pull = Pull.UP

encoder_btn = DigitalInOut(board.D2)
encoder_btn.direction = Direction.INPUT
encoder_btn.pull = Pull.UP


class SimpleEncoder:
    def __init__(self, pin_a, pin_b):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.last_state = (self.pin_a.value, self.pin_b.value)
        self.position = 0

    def update(self):
        state = (self.pin_a.value, self.pin_b.value)
        if state == self.last_state:
            return 0

        a_last, b_last = self.last_state
        a_now, b_now = state
        delta = 0

        if a_last == a_now:
            if b_now != b_last:
                delta = 1 if a_now != b_now else -1
        elif b_last == b_now:
            if a_now != a_last:
                delta = 1 if a_now == b_now else -1

        self.position += delta
        self.last_state = state
        return delta


enc = SimpleEncoder(encoder_a, encoder_b)
last_pos = enc.position

print("Rotate encoder, press button…")

while True:
    delta = enc.update()
    if delta != 0:
        print("Position:", enc.position, "delta:", delta)

    if not encoder_btn.value:
        print("Button pressed!")
        while not encoder_btn.value:
            time.sleep(0.02)

    time.sleep(0.01)