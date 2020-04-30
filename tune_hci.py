from audio_receiver import AudioReceiver
from frequency_finder import FrequencyFinder
from morpheme_listener import MorphemeListener
from note_detector import NoteDetector
from time import sleep


morpheme = [
    {
        'frequency': {
            'value': None,
            'duration_range': None,
            'diff_from_previous': {
                'min_semitones': 4,
                'max_semitones': 6
            }
        },
        'time': {
            'since_previous': 2,
            'since_first': 2
        }
    },
    {
        'frequency': {
            'value': None,
            'duration_range': None,
            'diff_from_previous': {
                'min_semitones': 2,
                'max_semitones': 4
            }
        },
        'time': {
            'since_previous': 3,
            'since_first': 10
        }
    }
]

def mcallback():
    print('morpheme got got')

morpheme_listener = MorphemeListener(morpheme_structure=morpheme, output=mcallback)
note_detector = NoteDetector(output=morpheme_listener.input_phoneme)
frequency_finder = FrequencyFinder(output=note_detector.input_frequency)
audio_receiver = AudioReceiver(output=frequency_finder.input_audio)
audio_receiver.start()

sleep(3000)
audio_receiver.stop()