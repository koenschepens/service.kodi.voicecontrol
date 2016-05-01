import json
import os

__author__ = 'macbook'

class PersonalAssistantBase():
    def __init__(self, context):
        self.context = context
        self._is_open = False
        self._is_active = False
        self._is_listening = False

    def ask_text(self, what):
        print("you said: " + what)

    def open(self, source_rate):
        raise NotImplementedError

    def send(self, in_data, frame_count):
        pass

    def is_open(self):
        return self._is_open

    def is_active(self):
        return self._is_active

    def is_listening(self):
        return self._is_listening

    def close(self):
        raise NotImplementedError

    def getresponse(self):
        return self.request.getresponse().read()

    def get_json_response(self):
        return json.loads(self.getresponse())

    def get_result(self):
        raise NotImplementedError

