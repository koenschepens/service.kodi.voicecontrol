import struct
import math
import sys
try:
    import audiotools
except:
    sys.path.append("/Applications/Kodi.app/Contents/Resources/Kodi/addons/service.kodi.voicecontrol/henk/includes/audiotools")
    import audiotools

import pyaudio

from audio_in_base import AudioInBase

FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100
CHUNK = 1024
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME

class PyAudio(AudioInBase):
    def __init__(self, context, input_sample_rate):
        self.input_sample_rate = input_sample_rate
        self.context = context
        self.threshold = self.context.config.getfloat("sound", "threshold") if self.context.config.has_option("sound", "threshold") else 0
        self.use_threshold = self.context.config.getboolean("sound", "use_threshold") if self.context.config.has_option("sound", "use_threshold") else True
        self.input_stream = None

    def find_input_device(self):
        device_index = None
        for i in range( self.pa.get_device_count() ):
            devinfo = self.pa.get_device_info_by_index(i)

            if devinfo["maxInputChannels"] > 0:
                device_index = i
                return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open(self, input_index = None, output_index = None):
        self.pa = pyaudio.PyAudio()

        self.input_device_index = self.find_input_device() if input_index is None else input_index
        self.context.log("Input device index: %s" % self.input_device_index)
        self.context.log("Input device sample rate: %s" % self.input_sample_rate)

    def close(self):
        self.stop()
        self.pa.terminate()

    def record(self, assistant_callback):
        self.silentcount = 0
        self.startedTalking = False

        def callback(in_data, frame_count, time_info, status):
            if(not self.use_threshold):
                is_listening = assistant_callback(in_data, frame_count)
                if(is_listening):
                    return (in_data, pyaudio.paContinue)
                else:
                    self.context.log("not listening")
                    return (in_data, pyaudio.paComplete)

            amplitude = self.get_rms(in_data)
            self.packagecount += 1

            self.startedTalking = True

            if(self.startedTalking):
                if(amplitude <= self.threshold):
                    self.silentcount += 1
                else:
                    self.silentcount = 0

                assistant_callback(in_data, frame_count)

                if(self.silentcount > int(self.context.config.get("sound", "wait_after_speak"))):
                    self.context.log("stopped listening...")
                    return (in_data, pyaudio.paComplete)

            return (in_data, pyaudio.paContinue)

        self.input_stream = self.pa.open(format = FORMAT,
                             channels = CHANNELS,
                             rate = self.input_sample_rate,
                             input = True,
                             input_device_index = self.input_device_index,
                             frames_per_buffer = INPUT_FRAMES_PER_BLOCK,
                             stream_callback = callback)

        self.input_stream.start_stream()

    def stop(self):
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.startedTalking = False
        self.silentcount = 0

    def is_active(self):
        return self.input_stream.is_active() if self.input_stream is not None else False

    def get_rms(self, block):
        # RMS amplitude is defined as the square root of the
        # mean over time of the square of the amplitude.
        # so we need to convert this string of bytes into
        # a string of 16-bit samples...

        # we will get one short out for each
        # two chars in the string.
        count = len(block)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, block )

        # iterate over the block.
        sum_squares = 0.0
        for sample in shorts:
            # sample is a signed short in +/- 32768.
            # normalize it to 1.0
            n = sample * SHORT_NORMALIZE
            sum_squares += n*n

        return math.sqrt( sum_squares / count )
