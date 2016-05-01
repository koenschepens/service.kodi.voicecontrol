import wave
import spotify
from spotify.sink import Sink


class PortAudioSink(Sink):

    """Audio sink for `PortAudio <http://www.portaudio.com/>`_.

    PortAudio is available for many platforms, including Linux, OS X, and
    Windows. This audio sink requires `PyAudio
    <https://pypi.python.org/pypi/pyaudio>`_.  PyAudio is probably packaged in
    your Linux distribution.

    On Debian/Ubuntu you can install PyAudio from APT::

        sudo apt-get install python-pyaudio

    Or, if you want to install PyAudio inside a virtualenv, install the
    PortAudio development headers from APT, then PyAudio::

        sudo apt-get install portaudio19-dev
        pip install --allow-unverified=pyaudio pyaudio

    On OS X you can install PortAudio using Homebrew::

        brew install portaudio
        pip install --allow-unverified=pyaudio pyaudio

    For an example of how to use this class, see the :class:`AlsaSink` example.
    Just replace ``AlsaSink`` with ``PortAudioSink``.
    """

    def __init__(self, session):
        self._session = session

        import pyaudio  # Crash early if not available
        self._pyaudio = pyaudio
        self._device = self._pyaudio.PyAudio()
        self._stream = None

        self.on()

    def _on_music_delivery(self, session, audio_format, frames, num_frames):
        assert (audio_format.sample_type == spotify.SampleType.INT16_NATIVE_ENDIAN)

        if self._stream is None:
            self._stream = self._device.open(
                format=self._pyaudio.paInt16, channels=audio_format.channels,
                rate=audio_format.sample_rate, output=True)

        # XXX write() is a blocking call. There are two non-blocking
        # alternatives:
        # 1) Only feed write() with the number of frames returned by
        # self._stream.get_write_available() on each call. This causes buffer
        # underruns every third or fourth write().
        # 2) Let pyaudio call a callback function when it needs data, but then
        # we need to introduce a thread safe buffer here which is filled when
        # libspotify got data and drained when pyaudio needs data.
        self._stream.write(frames, num_frames=num_frames)
        return num_frames

    def _close(self):
        if self._stream is not None:
            self._stream.close()
            self._stream = None
