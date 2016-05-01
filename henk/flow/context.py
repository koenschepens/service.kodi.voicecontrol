import os
import sys
import time
import threading

from states.initial import Initial

class Context():
    media_engine = None
    tts_engine = None
    speech_recognition_engine = None
    personal_assistant = None
    input_engine = None
    audio_in_engine = None
    audio_out_engine = None
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
        if(self.media_engine is not None):
            self.media_engine.log(message)
        else:
            print(message)

    def is_up(self, initial = False):
        return self.input_engine.is_up(initial)

    def run(self):
        self.state.go()

    # Uses the sound engine to ask the personal assistant something or if message is not None, sends the text to the
    # personal assistant. Is called from the phoneUp state.
    def ask(self, message = None):
        talking_count = 0

        while(self.is_talking()):
            time.sleep(0.5)
            talking_count += 1
            if(talking_count % 20 == 0):
                self.log("Still talking please wait...")

        if(message is None):
            self.audio_in_engine.open()

            # Writes the stream from the sound engine to the personal assistant
            def audio_callback(in_data, frame_count):
                if(not self.personal_assistant.is_open()):
                    self.log("Starting assistant with input sample rate: %s (skipped first %s packages)" % (self.audio_in_engine.input_sample_rate, self.audio_in_engine.packagecount))
                    self.personal_assistant.open(self.audio_in_engine.input_sample_rate)
                self.personal_assistant.send(in_data, frame_count)

                return self.personal_assistant.is_listening()

            self.audio_in_engine.record(audio_callback)

            #wait until the audio engine is done
            while self.audio_in_engine.is_active():
                time.sleep(0.1)

            #wait for the response from the assistant
            while(self.personal_assistant.is_active()):
                time.sleep(0.01)

            #stop the audio engine
            self.audio_in_engine.stop()

            self.personal_assistant.close()
            self.audio_in_engine.close()
            return self.personal_assistant.get_result()
        else:
            return self.personal_assistant.ask_text(message)

    def is_talking(self):
        return self.talk_thread is not None and self.talk_thread.is_alive()

    def show_notification(self, title, message = ''):
        self.media_engine.show_notification(title, message)

    def say(self, message, output = "phone_out", asynchronous = False):
        self.audio_out_engine.set_output(self.config.getint("sound", output))

        method = self.tts_engine.speak
        args = (message, self.audio_out_engine)
        if(asynchronous):
            self.talk_thread = threading.Thread(target=method, args=args, kwargs={})
            self.talk_thread.start()
        else:
            method(*args)

    def user_input_required(self):
        return self.media_engine.user_input_required()