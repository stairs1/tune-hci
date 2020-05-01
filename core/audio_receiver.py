import numpy as np
import pyaudio
from threading import Thread
from time import sleep


class Defaults():
    AUDIO_CHUNK_SIZE = 800
    SAMPLE_FREQ = 16000
    NUM_CHANNELS = 1
    OUTPUT_FUNC = lambda *_: None


class AudioReceiver():
    """
    Opens an audio stream from the default system microphone.
    Pass output kwarg to receive audio data callbacks.
    """
    def __init__(self, chunk_size=None, sample_freq=None, output=None):
        self.chunk_size = chunk_size or Defaults.AUDIO_CHUNK_SIZE
        self.sample_freq = sample_freq or Defaults.SAMPLE_FREQ
        self.output_func = output or Defaults.OUTPUT_FUNC
        self.num_channels = Defaults.NUM_CHANNELS
        self.audio = pyaudio.PyAudio()
        self.open = False
        self.stream = None

    def _callback(self, data_in, frame_count, time, status):
        data = np.frombuffer(data_in, dtype=np.int16)
        self.output_func(data)
        return (None, pyaudio.paContinue)

    def start(self): 
        self.open = True
        def run():
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_freq,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._callback
            )

            # leave thread alive to keep audio listening
            while self.open:
                sleep(0.01)

        Thread(target=run).start()
    
    def stop(self):
        if self.open:
            self.audio.close(self.stream)
            self.open = False
