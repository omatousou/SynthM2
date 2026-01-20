import sounddevice as sd

class AudioEngine:
    def __init__(self, fs=44100):
        self.stream = sd.OutputStream(samplerate=fs, channels=1, dtype='int16')
        self.stream.start()

    def play(self, data):
        self.stream.write(data)

    def terminate(self):
        self.stream.stop()
        self.stream.close()