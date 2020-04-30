from audio_receiver import AudioReceiver
from frequency_finder import FrequencyFinder
from morpheme_listener import MorphemeListener
from morphemes import do_re_mi
from note_detector import NoteDetector


class Defaults():
    FREQ_LOWER_BOUND = 600
    FREQ_UPPER_BOUND = 2500
    LIGHT_LOWER_BOUND = 0
    LIGHT_UPPER_BOUND = 1023


class LightController():
    def __init__(self):
        self.keyphrase_detector = MorphemeListener(
            morpheme_structure=do_re_mi,
            output=self.detected_keyphrase
        )
        self.capture_colour = None
        self.colours = {
            'red': None,
            'green': None,
            'blue': None
        }
        self.scaling_factor = (
            (Defaults.LIGHT_UPPER_BOUND - Defaults.LIGHT_LOWER_BOUND)
            / (Defaults.FREQ_UPPER_BOUND - Defaults.FREQ_LOWER_BOUND)
        )
    
    def detected_keyphrase(self):
        """
        Once keyphrase detected, use the next 3 frequencies for colours.
        """
        print('detected keyphrase, listening for colours')
        self.capture_colour = 'red'
    
    def _map_frequency_to_colour(self, frequency):
        bounded_frequency = max(frequency, Defaults.FREQ_LOWER_BOUND)
        bounded_frequency = min(bounded_frequency, Defaults.FREQ_UPPER_BOUND)
        print(int(frequency), int(bounded_frequency))
        return (bounded_frequency - Defaults.FREQ_LOWER_BOUND) * self.scaling_factor
    
    def input_phonemes(self, duration, frequency):
        if not self.capture_colour:
            self.keyphrase_detector.input_phoneme(duration, frequency)
            return
        
        self.colours[self.capture_colour] = self._map_frequency_to_colour(frequency)
        if self.capture_colour == 'red':
            self.capture_colour = 'green'
        elif self.capture_colour == 'green':
            self.capture_colour = 'blue'
        elif self.capture_colour == 'blue':
            self.send_form_rgb()
            self.capture_colour = None
    
    def send_form_rgb(self):
        print(f"red: {self.colours['red']}, green: {self.colours['green']}, blue: {self.colours['blue']}")


light_controller = LightController()
note_detector = NoteDetector(output=light_controller.input_phonemes)
frequency_finder = FrequencyFinder(output=note_detector.input_frequency)
audio_receiver = AudioReceiver(output=frequency_finder.input_audio)
audio_receiver.start()
