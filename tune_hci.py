from audio_receiver import AudioReceiver
from frequency_finder import FrequencyFinder
from note_detector import NoteDetector
from time import sleep

def callback(duration, freq):
    print(f'duration: {duration} f: {freq}')

def ffcallback(data):
    print(data)

note_detector = NoteDetector(output=callback)
frequency_finder = FrequencyFinder(output=note_detector.input_frequency)
audio_receiver = AudioReceiver(output=frequency_finder.input_audio)
audio_receiver.start()

sleep(3000)
audio_receiver.stop()