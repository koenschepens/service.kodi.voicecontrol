__author__ = 'macbook'

class AudioInBase():
    packagecount = 0
    def __init__(self, context):
        self.context = context

    def record(self, assistant_callback):
        raise NotImplementedError
