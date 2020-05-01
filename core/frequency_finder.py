import numpy as np


class Defaults():
    AUDIO_CHUNK_SIZE = 800
    SAMPLE_FREQ = 16000
    LOWER_BOUND = 400
    UPPER_BOUND = 4000
    OUTPUT_FUNC = lambda *_: None
    SNR_THRESHOLD = 80


class FrequencyFinder():
    """
    Synchronous processing pipeline on audio stream to find dominant frequency.

    Pipeline components:
        1. Power spectral density
        2. Bandpass filter to range of human whistle
        3. Select highest-power frequency
        4. Threshold to minumum 40 SNR; peak power should be >40x mean power.

    To use, connect input to audio stream, output to note detector.
    Small audio chunk sizes will result in imprecise frequency readings.
    """
    def __init__(self, output=None):
        self.chunk_size = Defaults.AUDIO_CHUNK_SIZE
        self.sample_f = Defaults.SAMPLE_FREQ
        self.lower_bound = Defaults.LOWER_BOUND
        self.upper_bound = Defaults.UPPER_BOUND
        self.output = output or Defaults.OUTPUT_FUNC
        self.snr_threshold = Defaults.SNR_THRESHOLD

    def input_audio(self, audio_raw):
        power, freqs = self._psd(audio_raw)
        bandpass_power, bandpass_freqs = self._bandpass(power, freqs)
        loudest_frequency = self._threshold(bandpass_power, bandpass_freqs)
        self.output(loudest_frequency)

    def _psd(self, data):
        power = np.abs(np.fft.fft(data))**2
        freqs = np.fft.fftfreq(data.size, 1 / self.sample_f)
        return power, freqs
    
    def _bandpass(self, power, freqs):
        power = power[(freqs > self.lower_bound) * (freqs < self.upper_bound)]
        freqs = freqs[(freqs > self.lower_bound) * (freqs < self.upper_bound)]
        return power, freqs
    
    def _threshold(self, bandpass_power, bandpass_freqs):
        if np.max(bandpass_power) / np.mean(bandpass_power) < self.snr_threshold:
            return None
        
        return bandpass_freqs[np.argmax(bandpass_power)]
