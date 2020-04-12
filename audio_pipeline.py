from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure
import numpy as np
import pyaudio
from time import sleep
import tkinter


class CircleBuf():
    """
    Wrapper over numpy array to dump streams to be animated.
    Can use as circular buffer via add_data, or manually set x & y.
    """
    def __init__(self, xstart, xfin, length, name=None):
        self.x = np.linspace(xstart, xfin, length)
        self.y = np.zeros(length)
        self.length = length
        self.name = name

    def add_data(self, data):
        self.y = np.insert(self.y, 0, data)[:self.length]


class BufferAnimation():
    def __init__(self, buffers):
        self.buffers = buffers
        self.fig = matplotlib.figure.Figure()
        self.fig.set_facecolor((0.85, 0.85, 0.85))
        self.grid_spec = self.fig.add_gridspec(2, 2)

        # add more plots here
        ax1 = self.fig.add_subplot(self.grid_spec[0, 0])
        ax1.set_fc((0.3, 0.3, 0.3, 1))
        ax2 = self.fig.add_subplot(self.grid_spec[0, 1])
        ax2.set_fc((0.3, 0.3, 0.3, 1))
        self.axes = ax1, ax2

        # config matplotlib tk backend for animation
        self.root = tkinter.Tk()
        self.root.wm_title("Audio Pipeline")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.canvas.draw()

    def draw(self):
        for i, axis in enumerate(self.axes):
            axis.clear()
            axis.plot(self.buffers[i].x, self.buffers[i].y, color=(1, 0.8, 0, 1))
            axis.set_title(buffers[i].name)

        self.canvas.draw()
        self.root.update()


raw_buffer = CircleBuf(0, 6, 96000, name='Raw Audio')
psd_buffer = CircleBuf(20, 800, 0, name='Power Spectral Density')
buffers = [raw_buffer, psd_buffer]
buffer_animation = BufferAnimation(buffers)


def psd(data, sample_f):

    psd = np.abs(np.fft.fft(data))**2
    frequencies = np.fft.fftfreq(data.size, 1 / sample_f)
    return [psd, frequencies]


def callback(data_in, frame_count, time, status):
    data = np.frombuffer(data_in, dtype=np.int16)

    # show raw audio over time
    buffers[0].add_data(data)

    # show psd instantaneously
    power, freq = psd(data, 16000)
    buffers[1].x = freq[freq > 20]
    buffers[1].y = power[freq > 20]

    return (None, pyaudio.paContinue)


audio = pyaudio.PyAudio()
stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1000,
    stream_callback=callback
)

while True:
    sleep(0.01)
    try:
        buffer_animation.draw()
    except tkinter.TclError:
        print('bye!')
        break
