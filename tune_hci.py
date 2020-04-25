from audio_receiver import AudioReceiver
from frequency_finder import FrequencyFinder
from note_detector import NoteDetector
from time import sleep

def callback(start, stop, freq):
    print(f'start: {start} stop: {stop} duration: {stop - start} f: {freq}')

note_detector = NoteDetector(output=callback)
frequency_finder = FrequencyFinder(output=note_detector.input_frequency)
audio_receiver = AudioReceiver(output=frequency_finder.input_audio)
audio_receiver.start()

sleep(30)
audio_receiver.stop()