import resampler
from program.flow.engines import PersonalAssistantBase, AssistentResult

actionMapper = {
    "NoResultCommand" : "wisdom.unknown",
    "WikipediaCommand" : "browser.open",
    "WeatherCommand" : "weather.search"
}

from program.includes.houndify import HoundListener, StreamingHoundClient, TextHoundClient


class HoundifyEngine(PersonalAssistantBase, HoundListener):
    def __init__(self, context):
        PersonalAssistantBase.__init__(self, context)
        self.client_id = context.config.get("houndify", "client_id")
        self.client_key = context.config.get("houndify", "client_key")
        self._result = None
        self.finished_handler = None

    def ask_text(self, what):
        self.client = TextHoundClient(self.client_id, self.client_key)
        return self.client.query(what)

    def is_active(self):
        active = self._result is None

        print(str(self) + " > " + str(active))

        return active

    def open(self, source_rate):
        self.client = StreamingHoundClient(self.client_id, self.client_key, sampleRate=16000)
        self.vad = resampler.VAD()
        self.resampler = resampler.Resampler(source_samplerate=source_rate)
        self.client.setLocation(37.388309, -121.973968)
        self._active = True
        self.client.start(self)

    def send(self, in_data, frame_count):
        frames, data = self.resampler.resample(in_data, frame_count)
        state = self.vad.processFrame(frames)
        self.client.fill(data)
        return data, state

    def close(self):
        self.client.finish()
        pass

    def getresponse(self):
        return self.outputString

    def get_result(self):
        return self._result

    def onPartialTranscript(self, transcript):
        print(transcript)
        pass

    def onFinalResponse(self, response):
        string = response["AllResults"][0]["SpokenResponseLong"]
        self.outputString = string
        result = HoundifyResult(response)

        print(str(self))
        print("done. result: " + str(result))
        self._result = result

    def onTranslatedResponse(self, response):
        print "Translated response: " + response

    def onError(self, err):
        print "ERROR"

class HoundifyResult(AssistentResult):
    def __init__(self, response):
        if("AllResults" in response):
            allresults = response["AllResults"][0]
            self.Text = allresults["SpokenResponseLong"]
            self.Action = actionMapper[allresults["CommandKind"]]
            if("NativeData" in allresults and "URI" in allresults["NativeData"][0]):
                self.Parameters["url"] = allresults["NativeData"][0]["URI"]

            self.SpokenResponse = allresults["SpokenResponse"]
            self.Hints = allresults["Hints"]
