import os
import time
from ..audio_out.audio_out_base import AudioOutBase

class Mpg123(AudioOutBase):
    supported_formats = ["mp3"]

    def play_mp3(self, path):
        os.system("mpg123 " + path)
