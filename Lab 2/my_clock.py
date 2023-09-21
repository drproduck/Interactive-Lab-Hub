import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import os

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
rotation = 90

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

start_time = time.time()

nb_images = len(os.listdir('output_images'))

# these setup the code for our buttons
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# Fix the total time for now
minutes_total = 1
seconds_total = 20

def remaining_time(seconds_total, seconds_elapsed):
    if seconds_elapsed >= seconds_total:
        return "00:00"  # Time has already elapsed
    seconds_remaining = seconds_total - int(seconds_elapsed)
    minutes, seconds = divmod(seconds_remaining, 60)
    return f"{minutes:02}:{seconds:02}"


fontsize = 30

def run_clock():
    time_start = time.time()

    while True:
        if not buttonB.value and buttonA.value:  # just button B pressed
            return

        seconds_elapsed = time.time() - time_start

        # Display the frame relative to the time elapsed
        frame_index = int(seconds_elapsed / seconds_total * nb_images)
        frame_index = min(frame_index, nb_images - 1)
        image = Image.open(os.path.join('output_images', f'frame_{frame_index}.png'))

        # If time's up, display "Time's up!"
        if seconds_elapsed > seconds_total:
            text = "Time's up!"
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fontsize)

            draw = ImageDraw.Draw(image, 'RGBA')
            draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0, 125))
            draw.text((40, (height - fontsize) // 2), text, font=font, fill="#FFFFFF")

        # Display the remaining time if button A is pressed
        if buttonB.value and not buttonA.value:  # just button A pressed
            text = remaining_time(seconds_total, seconds_elapsed)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fontsize)

            draw = ImageDraw.Draw(image, 'RGBA')
            draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0, 125))
            draw.text((75, (height - fontsize) // 2), text, font=font, fill="#FFFFFF")

        disp.image(image, rotation)
        time.sleep(1 / 60)

while True:
    run_clock() 
