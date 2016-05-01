import json
from henk.flow.actions.smalltalk import smalltalk
from henk.flow.actions.configActionState import configActionState
from henk.flow.actions.weather import weather
from henk.flow.media_command.command_factory import get_command
import resampler
from personal_assistent_base import PersonalAssistantBase
from ...media_command.media_command_base import *

from includes.houndify.houndify import HoundListener, StreamingHoundClient, TextHoundClient

class HoundifyEngine(PersonalAssistantBase, HoundListener):
    def __init__(self, context):
        PersonalAssistantBase.__init__(self, context)
        self.client_id = context.config.get("houndify", "client_id")
        self.client_key = context.config.get("houndify", "client_key")
        self._result = None
        self._is_open = False
        self._is_active = False
        self.finished_handler = None
        self.context = context
        self.transcript = None

    def ask_text(self, what):
        self.client = TextHoundClient(self.client_id, self.client_key, self.context.config.get("houndify", "userId"))
        houndresult = self.client.query(what)
        return self.create_command(json.loads(houndresult))

    def open(self, source_rate):
        self.client = StreamingHoundClient(self.client_id, self.client_key, sampleRate=self.context.config.getint("houndify", "samplerate"))
        self.vad = resampler.VAD()
        self.resampler = resampler.Resampler(source_samplerate=source_rate, destination_samplerate=self.context.config.getint("houndify", "samplerate"))
        self.client.setLocation(37.388309, -121.973968)
        self._is_open = True
        self._is_active = True
        self._is_listening = False
        self.client.start(self)

    def send(self, in_data, frame_count):
        frames, data = self.resampler.resample(in_data, frame_count)
        state = self.vad.processFrame(frames)
        self._is_listening = not self.client.fill(data)
        return data, state

    def close(self):
        self.client.finish()
        self._is_open = False
        self._is_active = False
        pass

    def getresponse(self):
        return self.outputString

    def get_result(self):
        return self._result

    def onPartialTranscript(self, transcript):
        self.transcript = transcript
        self.context.log(transcript)
        pass

    def onFinalResponse(self, response):
        string = response["AllResults"][0]["SpokenResponseLong"]
        self.outputString = string
        result = self.create_command(response)

        print("done. result: " + str(result))
        self._result = result
        self._is_active = False

    def onTranslatedResponse(self, response):
        print "Translated response: " + response

    def onError(self, err):
        print "ERROR"

    def create_command(self, response):
        if("AllResults" in response):
            allresults = response["AllResults"][0]

            command = self.create_media_command(allresults)

            command.OriginalResult = str(response)
            command.Text = allresults["SpokenResponse"]

            if("NativeData" in allresults and len(allresults["NativeData"])):
                try:
                    if("URI" in allresults["NativeData"][0]):
                        command.Parameters["url"] = allresults["NativeData"][0]["URI"]
                except:
                    pass
            command.SpokenResponse = allresults["SpokenResponseLong"]
            command.Hints = allresults["Hints"] if "Hints" in allresults else None

        return command

    def create_media_command(self, allresults):
        actionMapper = {
            "NoResultCommand" : self.create_default_command("smalltalk", "handle", allresults),
            "WikipediaCommand" : self.create_default_command("browser", "open", allresults),
            "WeatherCommand" : self.create_default_command("weather", "search", allresults),
            "KnowledgeCommand" : self.create_default_command("browser", "open", allresults),
            "SmallTalkCommand" : self.create_default_command("smalltalk", "handle", allresults),
            "MusicCommand" : self.create_music_command(allresults),
            None: self.create_default_command("smalltalk", "handle", allresults)
        }

        return actionMapper[allresults["CommandKind"]] if allresults["CommandKind"] in actionMapper else "smalltalk.handle"

    def create_default_command(self, domain, domain_action, allresults):
        command = MediaCommand(domain, domain_action)
        return command

    def create_music_command(self, allresults):
        command = None
        if("MusicCommandKind" in allresults):
            if(allresults["MusicCommandKind"] == "MusicSearchCommand"):
                command = MediaCommand("music", "search")
                command.artist = allresults["NativeData"]["SearchParameters"]["FilteredByArtists"][0]["ArtistName"]
            else:
                command = MediaCommand("music", "play")

        return command
