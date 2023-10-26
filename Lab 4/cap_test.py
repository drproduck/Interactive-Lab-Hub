<<<<<<< HEAD
=======

>>>>>>> e3978c089d22a08b986f67576c4811d235044059
import time
import board
import busio

import adafruit_mpr121

i2c = busio.I2C(board.SCL, board.SDA)

mpr121 = adafruit_mpr121.MPR121(i2c)

while True:
    for i in range(12):
        if mpr121[i].value:
            print(f"Twizzler {i} touched!")
    time.sleep(0.25)  # Small delay to keep from spamming output messages.
