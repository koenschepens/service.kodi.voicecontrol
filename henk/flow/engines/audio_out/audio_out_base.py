import struct

__author__ = 'macbook'

class AudioOutBase():
    def __init__(self, context, samplerate):
        self.context = context
        self.samplerate = samplerate
        
    def play_dial_tone(self, output):
        raise NotImplementedError

    def play_beep(self, output):
        raise NotImplementedError

    def set_output(self, index):
        self.output_device_index = index

    def play_wav(self, path):
        raise NotImplementedError

    def play(self, path):
        if(path.endswith(".mp3")):
            self.play_mp3(path)
        elif(path.endswith(".ogg")):
            self.play_ogg(path)
        elif(path.endswith(".wav")):
            self.play_wav(path)

    def play_mp3(self, path):
        raise NotImplementedError

    def play_ogg(self, path):
        raise NotImplementedError