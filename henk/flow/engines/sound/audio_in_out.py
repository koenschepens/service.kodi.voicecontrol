import struct
import math
import wave
import time
import sys
try:
    import audiotools
except:
    sys.path.append("/Applications/Kodi.app/Contents/Resources/Kodi/addons/service.kodi.voicecontrol/henk/includes/audiotools")
    import audiotools
import pyaudio

from sound_base import SoundBase

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

__author__ = 'macbook'
class AudioInOut(SoundBase):
    def __init__(self, context, input_sample_rate):
        self.input_sample_rate = input_sample_rate
        self.context = context
        self.threshold = self.context.config.getfloat("sound", "threshold")

    def play_dial_tone(self, output):
        self.context.execute_script('aplay -D ' + self.context.config.get('output', output) + ' ' + self.context.includes_dir + '/sounds/beepbeep.wav')

    def play_beep(self, output):
        self.context.execute_script('aplay -D ' + self.context.config.get('output', output) + ' ' + self.context.includes_dir + '/sounds/tuut.wav')

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

    def find_input_device(self):
        device_index = None
        for i in range( self.pa.get_device_count() ):
            devinfo = self.pa.get_device_info_by_index(i)
            print( "Device %d: %s"%(i,devinfo["name"]) )

            if devinfo["maxInputChannels"] > 0:
                device_index = i
                return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def find_output_device(self):
        device_index = None
        for i in range( self.pa.get_device_count() ):
            devinfo = self.pa.get_device_info_by_index(i)
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for i in range( self.pa.get_device_count() ):
                if(devinfo["maxOutputChannels"] > 0):
                    print( "Found an output: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open(self, input_index = None, output_index = None):
        self.pa = pyaudio.PyAudio()

        self.input_device_index = self.find_input_device() if input_index is None else input_index
        self.output_device_index = self.find_output_device() if output_index is None else output_index

    def set_output(self, index):
        self.output_device_index = index

    def close(self):
        self.pa.terminate()

    def play_wav(self, path):
        wf = wave.open(path, 'rb')
        self.output_stream = self.pa.open(format = FORMAT,
                             channels = CHANNELS,
                             rate = RATE,
                             input = False,
                             output=True,
                             output_device_index=self.output_device_index,
                             frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        # read data (based on the chunk size)
        data = wf.readframes(CHUNK)

        # play stream (looping from beginning of file to the end)
        while data != '':
            # writing to the stream is what *actually* plays the sound.
            self.output_stream.write(data)
            data = wf.readframes(CHUNK)

        # cleanup stuff.
        self.output_stream.close()
        self.pa.terminate()

    def play(self, path):
        if(path.endswith(".mp3")):
            self.play_mp3(path)
        elif(path.endswith(".ogg")):
            self.play_ogg(path)
        elif(path.endswith(".wav")):
            self.play_wav(path)

    def play_mp3(self, path):
        file = audiotools.open(path)
        stream = file.to_pcm()

        self.output_stream = self.pa.open(format = FORMAT,
                             channels = CHANNELS,
                             rate = RATE,
                             input = False,
                             output=True,
                             output_device_index=self.output_device_index,
                             frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        # read data (based on the chunk size)
        data = stream.read(CHUNK)

        # play stream (looping from beginning of file to the end)
        while data != '':
            # writing to the stream is what *actually* plays the sound.
            self.output_stream.write(data)
            data = stream.read(CHUNK)

        # cleanup stuff.
        self.output_stream.close()
        self.pa.terminate()

    def play_ogg(self, path):
        try:
            file = audiotools.open(path)
            stream = file.to_pcm()
            self.context.log("play ogg using device {0}".format(self.output_device_index))
            self.output_stream = self.pa.open(format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = False,
                                 output = True,
                                 output_device_index=self.output_device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

            # read data (based on the chunk size)
            data = stream.read(CHUNK)

            # play stream (looping from beginning of file to the end)
            while data != '':
                # writing to the stream is what *actually* plays the sound.
                self.output_stream.write(data)
                data = stream.read(CHUNK)

            # cleanup stuff.
            self.output_stream.close()
            self.pa.terminate()
        except:
            import pygame
            pygame.init()
            song = pygame.mixer.Sound(path)
            clock = pygame.time.Clock()
            song.play()
            while pygame.mixer.get_busy():
                time.sleep(0.2)
            pygame.quit()

    def record(self, assistant_callback):
        self.silentcount = 0
        self.startedTalking = False

        def callback(in_data, frame_count, time_info, status):
            amplitude = self.get_rms(in_data)

            if(not self.startedTalking and amplitude > self.threshold):
                self.startedTalking = True
                self.context.log("started talking...")

            if(self.startedTalking):
                if(amplitude <= self.threshold):
                    self.silentcount += 1
                else:
                    self.silentcount = 0

                assistant_callback(in_data, frame_count)

                if(self.silentcount > int(self.context.config.get("sound", "wait_after_speak"))):
                    self.context.log("stopped talking...")
                    return (in_data, pyaudio.paComplete)

            return (in_data, pyaudio.paContinue)

        self.input_stream = self.pa.open(format = FORMAT,
                             channels = CHANNELS,
                             rate = RATE,
                             input = True,
                             input_device_index = self.input_device_index,
                             frames_per_buffer = INPUT_FRAMES_PER_BLOCK,
                             stream_callback = callback)

        self.input_stream.start_stream()

        while self.input_stream.is_active():
                time.sleep(0.1)

        self.input_stream.stop_stream()
        self.input_stream.close()
        self.startedTalking = False
        self.silentcount = 0
