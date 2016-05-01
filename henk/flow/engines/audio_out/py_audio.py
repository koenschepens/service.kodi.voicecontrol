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

from audio_out_base import AudioOutBase

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

class PyAudio(AudioOutBase):
    supported_formats = []

    def __init__(self, context, input_sample_rate):
        self.pa = pyaudio.PyAudio()
        self.input_sample_rate = input_sample_rate
        self.context = context
        self.threshold = self.context.config.getfloat("sound", "threshold")
        self.output_stream = None

        if(audiotools.MP3Audio.supports_to_pcm()):
            self.supported_formats.append("mp3")
        if(audiotools.VorbisAudio.supports_to_pcm()):
            self.supported_formats.append("ogg")
        if(audiotools.WaveAudio.supports_to_pcm()):
            self.supported_formats.append("wav")

    def play_dial_tone(self, output):
        self.context.execute_script('aplay -D ' + self.context.config.get('output', output) + ' ' + self.context.includes_dir + '/sounds/beepbeep.wav')

    def play_beep(self, output):
        self.context.execute_script('aplay -D ' + self.context.config.get('output', output) + ' ' + self.context.includes_dir + '/sounds/tuut.wav')

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
        self.input_device_index = self.find_input_device() if input_index is None else input_index
        self.output_device_index = self.find_output_device() if output_index is None else output_index

    def set_output(self, index):
        self.output_device_index = index

    def close(self):
        if(self.output_stream is not None):
            self.pa.close(self.output_stream)
        if(self.input_stream is not None):
            self.pa.close(self.input_stream)
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

    def play_mp3(self, path):
        file = audiotools.open(path)
        stream = file.to_pcm()

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

    def play_ogg(self, path):
        file = audiotools.open(path)
        stream = file.to_pcm()
        self.context.log("play ogg using device {0}".format(self.output_device_index))
        self.output_stream = self.pa.open(format = FORMAT,
                             channels = 2,
                             rate = RATE,
                             input = False,
                             output = True,
                             output_device_index = self.output_device_index,
                             frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        # read data (based on the chunk size)
        framelist = stream.read(CHUNK)

        data = framelist.to_bytes(False, True)

        # play stream (looping from beginning of file to the end)
        while data != '':
            # writing to the stream is what *actually* plays the sound.
            self.output_stream.write(data)
            data = stream.read(CHUNK)

        # cleanup stuff.
        self.output_stream.close()
        self.pa.terminate()
