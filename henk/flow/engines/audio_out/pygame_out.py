import time
from henk.flow.engines.audio_out.audio_out_base import AudioOutBase
import pygame

__author__ = 'macbook'

class PygameOut(AudioOutBase):
    supported_formats = ["ogg"]
    def play_ogg(self, path):
        pygame.init()
        song = pygame.mixer.Sound(path)
        song.play()
        while pygame.mixer.get_busy():
            time.sleep(0.2)
        pygame.quit()