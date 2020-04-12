from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure
import matplotlib.image
import numpy as np
import pyaudio
from threading import Thread
from time import sleep
import tkinter


class CircleBuf():
    """
    Wrapper over numpy array to dump streams to be animated.
    Can use as circular buffer via add_data, or manually set x & y.
    """
    def __init__(self, xstart=0, xstop=0, length=0, name=None):
        self.x = np.linspace(xstart, xstop, length)
        self.y = np.zeros(length)
        self.length = length
        self.name = name

    def add_data(self, data):
        self.y = np.insert(self.y, 0, data)[:self.length]


class BufferAnimation():
    """
    Don't use matplotlib animation. Use this instead, much easier
    """
    def __init__(self, *buffers):
        self.buffers = buffers
        self.fig = matplotlib.figure.Figure()
        self.fig.set_facecolor((0.85, 0.85, 0.85))
        self.grid_spec = self.fig.add_gridspec(3, 2, hspace=0.5, wspace=0.4)

        # add more plots here
        ax_raw = self.fig.add_subplot(self.grid_spec[0, 0])
        ax_psd = self.fig.add_subplot(self.grid_spec[0, 1])
        ax_tone = self.fig.add_subplot(self.grid_spec[1, 0])
        ax_lowpass = self.fig.add_subplot(self.grid_spec[1, 1])
        ax_target = self.fig.add_subplot(self.grid_spec[2, 0])
        self.ax_image = self.fig.add_subplot(self.grid_spec[2, 1])
        self.animated_axes = ax_raw, ax_psd, ax_tone, ax_lowpass
        for ax in self.animated_axes:
            ax.set_fc((0.3, 0.3, 0.3, 1))

        # plot-specific configs
        ax_psd.set_yscale('log')
        ax_psd.set_ylim(0.1, 10E12)
        ax_tone.set_ylabel('Hz')
        ax_tone.set_ylim(0, 4000)
        ax_lowpass.set_ylabel('Hz')
        ax_lowpass.set_ylim(0, 4000)

        # static displays
        target_x = np.linspace(0, BUFFER_LEN_SECONDS, 192)
        target_y = np.zeros(192)
        target_y[:30] = 1100
        target_y[30:60] = 2000
        target_y[60:90] = 1500
        ax_target.set_fc((0.3, 0.3, 0.3, 1))
        ax_target.set_ylabel('Hz')
        ax_target.set_ylim(0, 4000)
        ax_target.plot(target_x, target_y, color=(1, 0.8, 0, 1))
        ax_target.set_title('Target Waveform')
        self.target_y = target_y
        self.closed = matplotlib.image.imread('closed.png')
        self.open = matplotlib.image.imread('open.png')
        self.ax_image.xaxis.set_ticks_position('none')
        self.ax_image.xaxis.set_ticklabels('')
        self.ax_image.yaxis.set_ticks_position('none')
        self.ax_image.yaxis.set_ticklabels('')
        self.ax_image.imshow(self.closed)

        # config matplotlib tk backend for animation
        self.root = tkinter.Tk()
        self.root.wm_title("Audio Pipeline")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.canvas.draw()

    def draw(self):
        for i, axes in enumerate(self.animated_axes):
            axes.lines = []
            axes.plot(self.buffers[i].x, self.buffers[i].y, color=(1, 0.8, 0, 1))
            axes.set_title(self.buffers[i].name)

        self.canvas.draw()
        self.root.update()


SAMPLE_FREQ = 16000
AUDIO_CHUNK_SIZE = 500
BUFFER_LEN_SECONDS = 6
LOWPASS_WINDOW_SIZE = 4
raw_buffer = CircleBuf(
    xstart=0,
    xstop=BUFFER_LEN_SECONDS,
    length=BUFFER_LEN_SECONDS*SAMPLE_FREQ,
    name='Raw Audio'
)
psd_buffer = CircleBuf(name='Power Spectral Density')
tone_buffer = CircleBuf(
    xstart=0,
    xstop=BUFFER_LEN_SECONDS,
    length=int((BUFFER_LEN_SECONDS * SAMPLE_FREQ) / AUDIO_CHUNK_SIZE),
    name='Thresholded Dominant Frequency'
)
lowpass_buffer = CircleBuf(
    xstart=int(((LOWPASS_WINDOW_SIZE - 1) * AUDIO_CHUNK_SIZE) / SAMPLE_FREQ),
    xstop=BUFFER_LEN_SECONDS,
    length=tone_buffer.length - (LOWPASS_WINDOW_SIZE - 1),
    name='TDF, Low-Pass Filtered'
)
buffer_animation = BufferAnimation(raw_buffer, psd_buffer, tone_buffer, lowpass_buffer)


def psd(data, sample_f):
    """
    Only interested in positive frequency components in range of human hearing.
    """
    psd = np.abs(np.fft.fft(data))**2
    frequencies = np.fft.fftfreq(data.size, 1 / sample_f)
    return [psd[frequencies > 20], frequencies[frequencies > 20]]


def lowpass(buffer, window_len):
    return np.average(buffer.y[:window_len])


def threshold(data, thresh_value):
    threshed = np.array(data)
    threshed[threshed < thresh_value] = 0
    return threshed


def compare_target(data, target):
    diff = sum(np.abs(target - data))
    close_enough = diff < 40000
    return close_enough


def show_success():
    buffer_animation.ax_image.imshow(buffer_animation.open)
    sleep(5)
    buffer_animation.ax_image.imshow(buffer_animation.closed)


def callback(data_in, frame_count, time, status):
    data = np.frombuffer(data_in, dtype=np.int16)

    # show raw audio over time
    raw_buffer.add_data(data)

    # show psd instantaneously
    power, freq = psd(data, SAMPLE_FREQ)
    thresh_power = threshold(power, 5E8)
    psd_buffer.x = freq
    psd_buffer.y = power

    # add main frequency over time
    tone_buffer.add_data(freq[np.argmax(thresh_power)])

    # add lowpass over time. Lowpass doesn't seem to be necessary, may exclude
    lowpass_buffer.add_data(lowpass(tone_buffer, LOWPASS_WINDOW_SIZE))

    if(compare_target(tone_buffer.y, buffer_animation.target_y)):
        print('\n\nGOTCHA\n\n')
        Thread(target=show_success).start()

    return (None, pyaudio.paContinue)


audio = pyaudio.PyAudio()
stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_FREQ,
    input=True,
    frames_per_buffer=AUDIO_CHUNK_SIZE,
    stream_callback=callback
)

while True:
    sleep(0.01)
    try:
        buffer_animation.draw()
    except tkinter.TclError:
        print('bye!')
        break
