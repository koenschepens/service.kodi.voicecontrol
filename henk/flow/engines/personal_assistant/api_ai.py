import json
import os
import re

import apiai

from ...media_command.media_command_base import MediaCommand, ImmediateResult
from ...media_command.command_factory import get_command
from personal_assistent_base import PersonalAssistantBase

class ApiAi(PersonalAssistantBase):
    result = None
    def __init__(self, context):
        PersonalAssistantBase.__init__(self, context)
        self.client_access_token = context.config.get('aiapi', 'client_access_token')
        self.subscription_key = context.config.get('aiapi', 'subscription_key')

        self.Api = apiai.ApiAI(self.client_access_token, self.subscription_key)
        self._is_open = False
        self.request = None

    def is_active(self):
        return False

    def get_result(self):
        if(self.request is not None):
            api_response = self.request.getresponse()
            json_result = json.loads(api_response.read())
            self.context.log(str(json_result))
            self.result = self.create_command(json_result)
        return self.result

    def ask_text(self, what):
        if(len(what) == 0):
            self.result = MediaCommand("Sorry, I didn't hear you")
            return self.result

        self.Request = what
        immediateActions = self.context.config.options("immediateActions")

        if(self.Request in immediateActions):
            configValue = self.context.config.get("immediateActions", self.Request)

            action = re.search('(\w*)\((\w*)\)', configValue)
            method_name = action.group(1)
            params = action.group(2)
            immediateResult = ImmediateResult()
            method = getattr(ImmediateResult, method_name)
            if not method:
                raise Exception("Method %s not implemented" % method_name)

            return method(immediateResult, params)

        request = self.Api.text_request()

        request.query = what
        response = request.getresponse()
        leJson = response.read()

        parsed_json = json.loads(leJson)

        self.result = self.create_command(parsed_json)

        return self.result

    def open(self, source_rate = 44100):
        self.vad = apiai.VAD()
        self.resampler = apiai.Resampler(source_samplerate=source_rate)

        self.request = self.Api.voice_request()
        self.request.lang = 'en' # optional, default value equal 'en'
        self._is_open = True

    def is_open(self):
        return self._is_open

    def send(self, in_data, frame_count):
        frames, data = self.resampler.resample(in_data, frame_count)
        state = self.vad.processFrame(frames)
        self.request.send(data)

        return data, state

    def close(self):
        self._is_open = False
        pass

    def create_command(self, response):
        if('parameters' in response['result']):
            parameters = response['result']['parameters']
        else:
            parameters = {}

        if('action' in response['result']):
            action = response['result']['action']
            if(action == "media.music_play"):
                action = "music.play"
        else:
            action = "input.unknown"

        command = get_command(action.split('.')[0], action.split('.')[1], parameters)

        command.Id = 1000
        command.NextFunction = None
        command.NeedsUserInput = False
        command.IncludesDir = os.path.dirname(os.path.realpath(__file__)) + '/includes/'
        command.ResolvedQuery = response['result']['resolvedQuery']
        command.Text = response['result']['fulfillment']['speech']
        command.SpokenResponse = command.Text if len(command.Text) > 0 else None
        command.ParsedJson = response
        command.assistent_response = response["html"] if "html" in response else None
        command.search_query = parameters["q"] if "q" in parameters else None
        command.artist = parameters["artist"] if "artist" in parameters else None

        def other(command):
            if(command.Text is not None):
                return command.show_notification(command.ResolvedQuery, command.Text, 600)
            else:
                return command.show_notification(command.ResolvedQuery, "Me no understand", 601)

        return command
        #self.Action = actionMapper[allresults["CommandKind"]] if allresults["CommandKind"] in actionMapper else "smalltalk.handle"
