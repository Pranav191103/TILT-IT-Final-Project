# accel_test.py – ADXL345 accelerometer test
import time
import board
import adafruit_adxl34x

i2c = board.I2C()
accel = adafruit_adxl34x.ADXL345(i2c)

print("ADXL345 test – printing acceleration (m/s^2)")

while True:
    x, y, z = accel.acceleration
    print("X: {:.2f}  Y: {:.2f}  Z: {:.2f}".format(x, y, z))
    time.sleep(0.3)