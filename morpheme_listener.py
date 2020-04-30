import numpy as np
from time import time


class Defaults():
    SEMITONE_WIDTH_FACTOR = 2**(1/12) - 1


class MorphemeListener():
    """
    Listens for a sequence of f-t vector phonemes. Fires callback on detection.
    Morpheme specification structure:
        [
            {
                frequency: {
                    value: None or {
                        target: <hertz>,
                        range: <semitones>
                    },
                    duration_range: None or {
                        min: <seconds or None>,
                        max: <seconds or None>
                    }
                    diff_from_previous: None or {
                        min_semitones: <semitones or None>,
                        max_semitones: <semitones or None>
                    }
                },
                time: {
                    since_previous: <seconds>,
                    since_first: <seconds>
                }
            }
        ]
    """
    def __init__(self, morpheme_structure, output=None):
        self.morpheme_structure = morpheme_structure
        self.output = output
        self.phoneme_index = 0
        self.start_time = None
        self.prev_time = None
        self.prev_freq = None

    def _reset(self):
        self.start_time = None
        self.prev_time = None
        self.prev_freq = None
        self.phoneme_index = 0
    
    def _check_time(self):
        target_time = self.morpheme_structure[self.phoneme_index]['time']
        if not target_time['since_previous'] or not target_time['since_first']:
            return True

        expired = (
            time() - self.prev_time > target_time['since_previous']
            or time() - self.start_time > target_time['since_first']
        )

        return not expired
    
    def _check_frequency(self, duration, frequency):
        target = self.morpheme_structure[self.phoneme_index]

        if target['frequency']['value']:
            raise NotImplementedError

        if target['frequency']['duration_range'] is not None:
            maximum = target['frequency']['duration_range']['max']
            minimum = target['frequency']['duration_range']['min']
            if maximum and duration > maximum:
                return False
            if minumum and duration < minimum:
                return False

        if target['frequency']['diff_from_previous'] is not None:
            max_diff = target['frequency']['diff_from_previous']['max_semitones']
            min_diff = target['frequency']['diff_from_previous']['min_semitones']
            semitone_size = np.mean([frequency, self.prev_freq]) * Defaults.SEMITONE_WIDTH_FACTOR
            semitone_diff = np.abs(frequency - self.prev_freq) / semitone_size
            print(f'semitone diff: {semitone_diff}')
            if not max_diff >= semitone_diff >= min_diff:
                return False

        return True
    
    def input_phoneme(self, duration, frequency):
        # no history when first phoneme received
        if not self.prev_freq:
            self.start_time = time()
            self.prev_time = time()
            self.prev_freq = frequency
            return
        
        recognized = self._check_time() and self._check_frequency(duration, frequency)
        if recognized:
            self.prev_freq = frequency
            self.prev_time = time()
            self.phoneme_index += 1
            if self.phoneme_index == len(self.morpheme_structure):
                self.output()
                self._reset()
        else:
            self.start_time = time()
            self.prev_time = time()
            self.prev_freq = frequency