__author__ = 'macbook'

class SoundBase():
    def __init__(self, context):
        self.context = context

    def play_dial_tone(self, output):
        pass

    def play_beep(self, output):
        pass

    def set_output(self, index):
        self.output_device_index = index