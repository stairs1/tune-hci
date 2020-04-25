import numpy as np
from time import time


class Defaults():
    MIN_DURATION = 0.2
    MAX_DURATION = 2
    LOWER_BOUND = 400
    UPPER_BOUND = 4000
    ACCEPTABLE_DEVIATION = 0.1
    INPUT_RATE = 80
    OUTPUT_FUNC = lambda *_: None


class NoteDetector():
    """
    Detects notes from a stream of frequency readings.
    A note is 200-2000ms of frequency readings that differ by less than 10%.

    Outputs note detections containing start time, end time, and frequency.
    """
    def __init__(self, output=None):
        self.acceptable_deviation = Defaults.ACCEPTABLE_DEVIATION
        self.min_readings = int(Defaults.MIN_DURATION * Defaults.INPUT_RATE)
        self.max_readings = int(Defaults.MAX_DURATION * Defaults.INPUT_RATE)
        self.readings = np.empty(self.max_readings)
        self.highest_reading = Defaults.LOWER_BOUND
        self.lowest_reading = Defaults.UPPER_BOUND
        self.readings_count = 0
        self.note_start = None
        self.output = output or Defaults.OUTPUT_FUNC

    def _detect_and_reset(self):
        frequency = np.mean(self.readings[:self.readings_count])
        self.readings_count = 0
        self.lowest_reading = Defaults.UPPER_BOUND
        self.highest_reading = Defaults.LOWER_BOUND
        self.output(self.note_start, time(), frequency)

    def input_frequency(self, frequency):
        if self.readings_count == 0:
            self.note_start = time()
        self.lowest_reading = min(frequency, self.lowest_reading)
        self.highest_reading = max(frequency, self.highest_reading)
        self.readings[self.readings_count] = frequency
        self.readings_count += 1

        deviant = (
            (self.highest_reading - self.lowest_reading) / self.highest_reading
            > self.acceptable_deviation
        )

        if deviant:
            if self.readings_count >= self.min_readings:
                self._detect_and_reset()
            elif self.readings_count < self.min_readings:
                self.readings_count = 1
                self.lowest_reading = frequency
                self.highest_reading = frequency
                self.note_start = time()
        elif self.readings_count == self.max_readings:
            self._detect_and_reset()
