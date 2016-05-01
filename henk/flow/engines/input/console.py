__author__ = 'macbook'

BOARD = 1
BCM = 2

IN = 100
OUT = 101
PUD_DOWN = 200
PUD_UP = 201

class Console():
    mode = BOARD

    def __init__(self, context):
        self.context = context

    def setmode(self, mode):
        self.mode = mode

    def setup(self, address, inout, pull_up_down = PUD_DOWN):
        pass

    def is_up(self, initial = False):
        if(initial):
            return True

        return self.input("hoorn") == 1

    def input(self, channel):
        value = raw_input("press enter to talk")

        return 1

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
