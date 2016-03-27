import os
import sys
from time import sleep
import threading

from program.flow.states.initial import Initial


class Context():
    target_engine = None
    tts_engine = None
    speech_recognition_engine = None
    personal_assistant = None
    input_engine = None
    sound_engine = None
    config = None
    language = None
    state = None
    talk_thread = None

    def __init__(self, config, root_folder, includes_dir, language):
        self.root_folder = root_folder
        self.includes_dir = includes_dir
        self.language = language
        self.config = config
        sys.path.append(root_folder)
        sys.path.append(os.path.join(self.root_folder, 'target'))
        self.state = Initial(self)

    def log(self, message):
        if(self.target_engine is not None):
            self.target_engine.log(message)
        else:
            print(message)

    def isUp(self):
        return self.input_engine.isUp()

    def run(self):
        self.state.go()

    # Uses the sound engine to ask the personal assistant something or if message is not None, sends the text to the
    # personal assistant. Is called from the phoneUp state.
    def ask(self, message = None):
        talking_count = 0

        while(self.is_talking()):
            sleep(0.5)
            talking_count += 1
            if(talking_count % 20 == 0):
                self.log("Still talking...")

        if(message is None):
            self.sound_engine.open()

            self.personal_assistant.open(self.sound_engine.input_sample_rate)

            # Writes the stream from the sound engine to the personal assistant
            def audio_callback(in_data, frame_count):
                self.personal_assistant.send(in_data, frame_count)

            self.sound_engine.record(audio_callback)
            self.sound_engine.close()

            while(self.personal_assistant.is_active()):
                #wait for the response from the assistant
                sleep(0.1)

            self.personal_assistant.close()
            return self.personal_assistant.get_result()
        else:
            return self.personal_assistant.ask_text(message)


    def is_talking(self):
        return self.talk_thread is not None and self.talk_thread.is_alive()

    def say(self, message, output = "phone_out", asynchronous = False):
        self.sound_engine.set_output(self.config.getint("sound", output))

        method = self.tts_engine.speak
        args = (message, self.sound_engine)
        if(asynchronous):
            self.talk_thread = threading.Thread(target=method, args=args, kwargs={})
            self.talk_thread.start()
        else:
            method(*args)

    def show_notification(self, title, message = ''):
        self.target_engine.show_notification(title, message)

    def user_input_required(self):
        return self.target_engine.user_input_required()

    def play_movie(self, result):
        params = result.Parameters
        if('title' in params and params['title'] != '$title'):
            q = params['title']
            self.target_engine.search_movie(q)
            url = 'plugin://plugin.video.kodipopcorntime/search?query=' + q + ''
        elif('searchQuery' in params and params['searchQuery'] != '$q'):
            q = params['searchQuery']
            url = 'plugin://plugin.video.kodipopcorntime/search?query=' + q + ''
        elif('genre' in params and params['genre'] != '$genre'):
            url = 'plugin://plugin.video.kodipopcorntime/genres/' + params['genre'] + '/1?limit=20'
        else:
            url = "plugin://plugin.video.kodipopcorntime/genres"

        container = self.context.activate_window(url, window='videos')

    def show_weather(self, location):
        self.target_engine.activate_window(pluginurl = None, window = "weather")

    def send_action(self, action):
        self.target_engine.send_action(action)