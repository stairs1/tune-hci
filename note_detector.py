import numpy as np
from time import time


class Defaults():
    MIN_DURATION = 0.25
    MAX_DURATION = 2
    SEMITONE_WIDTH_FACTOR = 2**(1/12) - 1
    INPUT_RATE = 20
    OUTPUT_FUNC = lambda *_: None


class NoteDetector():
    """
    Detects notes from a stream of frequency readings.
    A note is 250-2000ms of frequency readings that differ by less than a semitone.

    Outputs note detections containing frequency and duration.
    Synchronous.
    """
    def __init__(self, output=None):
        self.min_duration = int(Defaults.MIN_DURATION * Defaults.INPUT_RATE)
        self.max_duration = int(Defaults.MAX_DURATION * Defaults.INPUT_RATE)
        self.readings = np.empty(self.max_duration)
        self.duration = 0
        self.output = output or Defaults.OUTPUT_FUNC

    def _detect(self):
        duration_seconds = self.duration / Defaults.INPUT_RATE
        frequency = np.mean(self.readings[:self.duration])
        self.output(duration_seconds, frequency)
    
    def _reset(self):
        self.duration = 0

    def _frequency_is_deviant(self, frequency):
        """
        A frequency is deviant if there is more than a semitone difference
            between it and any frequency in a given note.
        """
        if self.duration == 0:
            return False

        mean_note_frequency = np.mean(self.readings[:self.duration])
        semitone_width = mean_note_frequency * Defaults.SEMITONE_WIDTH_FACTOR
        return np.max(np.abs(self.readings[:self.duration] - frequency)) > semitone_width

    def input_frequency(self, frequency):
        """
        Notes are detected when they end.
        The end of a note is an abscence of any frequency, 
            the presence of a deviant frequency, or duration reaching a maximum.
        A note must be sustained for a minimum duration to be detected.
        """
        # This frequency is not part of this note
        if not frequency or self._frequency_is_deviant(frequency):
            if self.duration >= self.min_duration:
                self._detect()
            self._reset()

        if frequency:
            self.readings[self.duration] = frequency
            self.duration += 1
            if self.duration == self.max_duration:
                self._detect()
                self._reset()
