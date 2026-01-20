import numpy as np

class SignalGenerator:
    def __init__(self, fs=44100):
        self.fs = fs

    def get_block(self, freqs, phases, duration, wave_type):
        t = np.linspace(0, duration, int(duration * self.fs), endpoint=False)
        
        sig = np.zeros_like(t)
        for freq in freqs:
            phase = phases[freq]
            if wave_type == "Sinus":
                sig += np.sin(2 * np.pi * freq * t + phase)
            elif wave_type == "Carré":
                sig += np.sign(np.sin(2 * np.pi * freq * t + phase))
            elif wave_type == "Dents de scie":
                sig += 2 * ((freq * t + phase / (2 * np.pi)) % 1) - 1
            else:
                sig += np.zeros_like(t)
        
        # Normalize by number of frequencies to avoid clipping
        if freqs:
            sig /= len(freqs)
            
        return t, (sig * 0.2 * 32767).astype(np.int16)