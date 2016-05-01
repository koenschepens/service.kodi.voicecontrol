from henk.flow.engines.audio_out.audio_out_base import AudioOutBase

__author__ = 'macbook'

class APlay(AudioOutBase):
    supported_formats = ["mp3","wav","ogg"]
    def __init__(self, context):
        self.context = context

    def play_dial_tone(self, output):
        self.context.execute_script('aplay -D ' + self.context.config.get('output', output) + ' ' + self.context.includes_dir + '/sounds/beepbeep.wav')

    def play_beep(self, output):
        self.context.execute_script('aplay -D ' +  + ' ' + self.context.includes_dir + '/sounds/tuut.wav')

    def set_output(self, index):
        self.output_device_index = index

    def play_wav(self, path):
        raise NotImplementedError

    def play(self, path):
        self.context.execute_script('aplay -D ' + self.context.config.get('output', output) + ' ' + self.context.includes_dir + '/sounds/beepbeep.wav')

    def play_mp3(self, path):
        raise NotImplementedError

    def play_ogg(self, path):
        raise NotImplementedError
