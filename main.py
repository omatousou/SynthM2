import sys
import numpy as np
from math import gcd
from fractions import Fraction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from generator import SignalGenerator
from audio_engine import AudioEngine
from interface import SynthInterface

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.gui = SynthInterface()
        self.audio = AudioEngine()
        self.gen = SignalGenerator()

        self.NOTES_MAP = {
            Qt.Key_A: 261.63, Qt.Key_Z: 293.66, Qt.Key_E: 329.63,
            Qt.Key_R: 349.23, Qt.Key_T: 392.00, Qt.Key_Y: 440.00, Qt.Key_U: 493.88
        }

        self.is_playing = False
        self.active_freqs = set()
        self.previous_freqs = set()
        self.waiting = False
        self.current_time = 0.0
        self.phase_accum = {}  # Phase accumulator for each frequency
        self.plot_buffer = []  # Buffer for plotting the sent signal

        self.timer = QTimer()
        self.timer.timeout.connect(self.play_block)

        # Connexion des signaux de l'interface
        self.gui.key_pressed.connect(self.on_press)
        self.gui.key_released.connect(self.on_release)
        self.gui.close_signal.connect(self.on_close)

    def on_press(self, key):
        if key in self.NOTES_MAP:
            freq = self.NOTES_MAP[key]
            self.active_freqs.add(freq)
            if freq not in self.phase_accum:
                # Synchronize phase with average of existing phases for smooth addition
                if self.phase_accum:
                    self.phase_accum[freq] = sum(self.phase_accum.values()) / len(self.phase_accum)
                else:
                    self.phase_accum[freq] = 0.0
            if not self.is_playing and self.active_freqs:
                self.is_playing = True
                self.timer.start(25)  # 25ms intervals

    def on_release(self, key):
        if key in self.NOTES_MAP:
            freq = self.NOTES_MAP[key]
            self.previous_freqs = self.active_freqs.copy()
            self.active_freqs.discard(freq)
            if not self.active_freqs:
                self.is_playing = False
                self.waiting = True
                # Continue playing the previous waveform until period ends
                # But since it's looped, we need to wait for one period
                # Calculate wait_time
                periods = [Fraction(1/f).limit_denominator(1000) for f in self.previous_freqs]
                if periods:
                    denoms = [p.denominator for p in periods]
                    common_d = 1
                    for d in denoms:
                        common_d = common_d * d // gcd(common_d, d)
                    nums = [p.numerator * (common_d // p.denominator) for p in periods]
                    lcm_num = nums[0]
                    for n in nums[1:]:
                        lcm_num = lcm_num * n // gcd(lcm_num, n)
                    lcm_p = Fraction(lcm_num, common_d)
                    lcm_period = float(lcm_p)
                    wait_time = lcm_period
                else:
                    wait_time = 0
                self.wait_timer = QTimer()
                self.wait_timer.setSingleShot(True)
                self.wait_timer.timeout.connect(self.end_wait)
                self.wait_timer.start(int(wait_time * 1000))
            # For partial release, update display
            elif self.is_playing:
                # Update display
                duration = 0.025
                t = np.linspace(0, duration, int(duration * self.gen.fs), endpoint=False)
                sig = np.zeros_like(t)
                for f in self.active_freqs:
                    sig += np.sin(2 * np.pi * f * t)
                sig /= len(self.active_freqs)
                audio_data = (sig * 0.2 * 32767).astype(np.int16)
                freq_text = ", ".join(f"{f:.1f}" for f in sorted(self.active_freqs))
                self.gui.update_display(t, audio_data, f"{freq_text} Hz")

    def play_block(self):
        if self.is_playing or self.waiting:
            freqs = list(self.previous_freqs if self.waiting else self.active_freqs)
            if freqs:
                duration = 0.05  # Very short blocks
                phases = {f: self.phase_accum[f] for f in freqs}
                t, audio_data = self.gen.get_block(
                    freqs, phases, duration, self.gui.combo.currentText()
                )
                # Update phases for next block
                for f in freqs:
                    self.phase_accum[f] += 2 * np.pi * f * duration
                self.current_time += duration
                self.audio.play(audio_data)
                # Accumulate for plotting the signal sent to speaker
                self.plot_buffer.extend(audio_data.tolist())
                max_samples = int(0.05 * self.gen.fs)  # 0.05 second display (oscilloscope window)
                if len(self.plot_buffer) > max_samples:
                    self.plot_buffer = self.plot_buffer[-max_samples:]
                # Fixed time scale for oscilloscope-like display
                t_plot = np.linspace(0, 0.05, len(self.plot_buffer))
                freq_text = ", ".join(f"{f:.1f}" for f in sorted(freqs))
                self.gui.update_display(t_plot, np.array(self.plot_buffer), f"{freq_text} Hz")

    def end_wait(self):
        self.waiting = False
        self.timer.stop()
        self.plot_buffer = []
        self.gui.update_display([0], [0], "Repos")

    def on_close(self):
        self.audio.terminate()

    def run(self):
        self.gui.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    ctrl = AppController()
    ctrl.run()