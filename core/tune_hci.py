from audio_receiver import AudioReceiver
from frequency_finder import FrequencyFinder
from morpheme_listener import MorphemeListener
from morphemes import low_high_med
from note_detector import NoteDetector
from utils import PrintLogger

from time import sleep

def mcallback():
    print('morpheme got got')


morpheme_listener = MorphemeListener(morpheme_structure=low_high_med, output=mcallback)
logger = PrintLogger(output=morpheme_listener.input_phoneme)
note_detector = NoteDetector(output=logger.input_to_log)
frequency_finder = FrequencyFinder(output=note_detector.input_frequency)
audio_receiver = AudioReceiver(output=frequency_finder.input_audio)
audio_receiver.start()

sleep(3000)
audio_receiver.stop()