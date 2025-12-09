# TILT-IT – TECHIN 512 Final Project

## Overview

TILT-IT is a 90s-style handheld electronic reaction game built with a
Seeed XIAO ESP32C3 and CircuitPython. The player holds the device and
responds to commands on the OLED screen using four types of moves:

- **SHAKE** – shake the device
- **LEFT** – turn the rotary encoder left
- **RIGHT** – turn the rotary encoder right
- **BUTTON** – press the rotary encoder button

If the right move is made within the time limit, the player goes to the
next level. If the move is wrong or too slow, it's *Game Over*.

---

## Hardware Used

Required components:

- Seeed XIAO ESP32C3 microcontroller
- SSD1306 128x64 I2C OLED display
- ADXL345 accelerometer (I2C)
- Rotary encoder with push button
- Single NeoPixel LED
- LiPo Battery
- Power switch (between battery and ESP32C3 board)
- Perfboard + female headers
- Jumper wires, heat-shrink tubing, etc.

All primary components are soldered to perfboard using female headers so
they can be removed and replaced if needed.

---

## Game Design

### Difficulty Levels

The game has **three difficulty settings**:

- **Easy** – longest time window per move  
- **Medium** – shorter time window  
- **Hard** – shortest time window  

The difficulty is shown on the OLED and selected using the rotary
encoder. Pressing the encoder button confirms the selection.

### Moves and Levels

- Minimum **four moves**: `SHAKE`, `LEFT`, `RIGHT`, `BUTTON`
- The game has at least **10 levels**
- Each level:
  1. Shows `Level N` and a random move on the OLED.
  2. Starts a timer (time limit depends on difficulty and level).
  3. Waits for player input from accelerometer / encoder / button.

If the input matches and is fast enough, the level number increases.  
If not, the game shows a **Game Over** screen.

If the player completes all levels, a **Game Win** screen is shown.

### Time Limit

The time limit is:

- Based on the difficulty level (`Easy`, `Medium`, `Hard`)
- Decreases slightly as levels increase (higher levels = faster game)

---

## NeoPixel Usage

The NeoPixel has multiple color states:

- **Idle / menu** – dim blue
- **During move** – dim green
- **Correct move** – flash bright green
- **Wrong move / Game Over** – red
- **Win** – simple color animation (green → blue → yellow)

---

## Accelerometer Calibration

The ADXL345 accelerometer is read using the CircuitPython library
`adafruit_adxl34x`. The game uses a simple threshold-based method to
detect a "SHAKE" move:

- The code reads the X, Y, Z acceleration.
- It computes a rough magnitude and compares it to a `SHAKE_THRESHOLD`.
- Only values above that threshold are treated as a real shake.

The threshold value can be tuned based on testing so that small noise
doesn't trigger a move, but an intentional shake does.

---

## Enclosure Design

The enclosure is a 3D-printed handheld case that:

- Holds the perfboard with all components
- Has:
  - A cutout for the OLED screen on the top
  - A hole for the NeoPixel to be visible from the top
  - A hole for the rotary encoder + knob
  - A hole / slot for the Type-C USB port (programming and power)
  - An accessible **On/Off** switch
- Has a removable side or lid to access electronics and LiPo battery.

(Images and CAD screenshots of the enclosure can be added here.)

---

## Repository Contents

- `src/code.py` – main TILT-IT game logic
- `src/oled_test.py` – OLED test (text display)
- `src/encoder_test.py` – rotary encoder + button test
- `src/accel_test.py` – accelerometer test
- `src/neopixel_test.py` – NeoPixel color test
- `lib/README.txt` – list of required CircuitPython libraries
- `Documentation/system-diagram.png` – system diagram (to be added)
- `Documentation/circuit-diagram.png` – circuit diagram (to be added)

---

## How to Run (conceptual)

1. Install CircuitPython for Seeed XIAO ESP32C3.
2. Copy the required `.mpy` libraries from the Adafruit CircuitPython
   Bundle into the `lib` folder on the board:
   - `adafruit_ssd1306.mpy`
   - `adafruit_bus_device/`
   - `adafruit_adxl34x.mpy`
   - `neopixel.mpy`
3. Copy `code.py` from the `src` folder to the root of the board.
4. Reset the board.  
   The splash screen should appear, then the difficulty select screen.

(For this class, the libraries and files are installed using the WiFi
Web API process described in Take Home Assignment 2.)

---

## Future Improvements / Extra Credit Ideas

- Add a **score system** that rewards faster responses.
- Add a **high score table** with initials stored in flash.
- Add a **piezo buzzer** for sound effects (correct/incorrect, win, etc.)
- Add an animated splash screen when the device first powers on.

## System Diagram
![System Diagram](Documentation/system-diagram.png)

## Circuit Diagram
![Circuit Diagram](Documentation/circuit-diagram.png)
