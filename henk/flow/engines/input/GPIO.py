__author__ = 'macbook'

import RPi.GPIO as gpio

class GPIO():
    def __init__(self, context):
        gpio.setmode(gpio.BCM)
        self.pin = context.config.getint("gpio", "hook")
        gpio.setup(self.pin, gpio.IN, pull_up_down = gpio.PUD_DOWN)

    def is_up(self):
        return gpio.input(self.pin)
