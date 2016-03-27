import json
import os
import re

import apiai

from flow.assistent_result.assistent import AssistentResult, ImmediateResult
from flow.assistent_result.apps import AppsResult
from personal_assistent_base import PersonalAssistantBase

class ApiAi(PersonalAssistantBase):
    result = None
    def __init__(self, context):
        PersonalAssistantBase.__init__(self, context)
        self.client_access_token = context.config.get('aiapi', 'client_access_token')
        self.subscription_key = context.config.get('aiapi', 'subscription_key')

        self.Api = apiai.ApiAI(self.client_access_token, self.subscription_key)

    def is_active(self):
        return False

    def get_result(self):
        if(self.request):
            api_response = self.request.getresponse()
            json_result = json.loads(api_response.read())
            self.context.log(str(json_result))
            self.result = self.create_result(json_result)
        return self.result

    def ask_text(self, what):
        if(len(what) == 0):
            self.result = AssistentResult("Sorry, I didn't hear you")
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

        self.result = AssistentResult(parsed_json, self.client_access_token, self.subscription_key)

        return self.result

    def open(self, source_rate = 44100):
        self.vad = apiai.VAD()
        self.resampler = apiai.Resampler(source_samplerate=source_rate)

        self.request = self.Api.voice_request()
        self.request.lang = 'en' # optional, default value equal 'en'

    def send(self, in_data, frame_count):
        frames, data = self.resampler.resample(in_data, frame_count)
        state = self.vad.processFrame(frames)
        self.request.send(data)

        return data, state

    def close(self):
        pass

    def create_result(self, json_result):
        if('action' in json_result['result']):
            action = json_result['result']['action']
        else:
            action = "input.unknown"

        if(action.startswith("apps")):
            result = AppsResult(action)
        else:
            result = AssistentResult()

        result.Id = 1000
        result.NextFunction = None
        result.NeedsUserInput = False
        result.Action = {}
        result.IncludesDir = os.path.dirname(os.path.realpath(__file__)) + '/includes/'
        result.ResolvedQuery = json_result['result']['resolvedQuery']
        result.Text = json_result['result']['fulfillment']['speech']
        result.SpokenResponse = result.Text if len(result.Text) > 0 else None
        result.ParsedJson = json_result
        result.assistent_response = json_result["html"] if "html" in json_result else None

        if('action' in json_result['result']):
            result.Action = json_result['result']['action']
        else:
            result.Action = "input.unknown"

        result.Parameters = {}
        if('parameters' in json_result['result']):
            result.Parameters = json_result['result']['parameters']

        return result