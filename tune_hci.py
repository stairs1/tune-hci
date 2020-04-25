from audio_receiver import AudioReceiver
from frequency_finder import FrequencyFinder
from time import sleep

def callback(data):
    print(data)

frequency_finder = FrequencyFinder(output=callback)
audio_receiver = AudioReceiver(output=frequency_finder.input_audio)
audio_receiver.start()

sleep(10)
audio_receiver.stop()