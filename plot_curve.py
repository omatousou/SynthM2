import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class SignalGenerator:
    def generate_note(self, freq, start_time, duration=0.05, wave_type="Sinus", fs=44100):
        """Génère un bloc en utilisant un vecteur temps continu (start_time)"""
        # Création du vecteur temps qui suit la progression réelle
        t = np.linspace(start_time, start_time + duration, int(duration * fs), endpoint=False)
        
        if wave_type == "Sinus":
            sig = np.sin(2 * np.pi * freq * t)
        elif wave_type == "Carré":
            sig = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == "Dents de scie":
            sig = 2 * ((freq * t) % 1) - 1
        else:
            sig = np.zeros_like(t)
            
        return t, (sig * 0.3 * 32767).astype(np.int16)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synthétiseur Sans Glitch - Phase Continue")
        self.resize(800, 400)

        self.fs = 44100
        # Utilisation d'un bloc de buffer plus petit pour la réactivité
        self.stream = sd.OutputStream(samplerate=self.fs, channels=1, dtype='int16', blocksize=1024)
        self.stream.start()

        self.NOTES_MAP = {
            Qt.Key_A: 261.63, Qt.Key_Z: 293.66, Qt.Key_E: 329.63,
            Qt.Key_R: 349.23, Qt.Key_T: 392.00, Qt.Key_Y: 440.00, Qt.Key_U: 493.88
        }

        self.generator = SignalGenerator()
        self.is_playing = False
        self.current_freq = None
        self.current_time = 0.0  # Variable cruciale pour la continuité
        
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.combo = QComboBox()
        self.combo.addItems(["Sinus", "Carré", "Dents de scie"])
        self.combo.setFocusPolicy(Qt.NoFocus)
        self.label_note = QLabel("Maintenez A Z E R T Y U")
        layout.addWidget(self.combo)
        layout.addWidget(self.label_note)
        self.win_plt = pg.GraphicsLayoutWidget()
        layout.addWidget(self.win_plt)
        self.curve = self.win_plt.addPlot().plot(pen='y')

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.NOTES_MAP and not event.isAutoRepeat():
            self.is_playing = True
            self.current_freq = self.NOTES_MAP[key]
            # On ne remet PAS self.current_time à zéro ici pour éviter le clic au changement de note rapide
            self.play_loop()

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.is_playing = False
            self.current_freq = None
            self.label_note.setText("Prêt...")
            self.curve.setData([], [])

    def play_loop(self):
        if self.is_playing and self.current_freq:
            duration = 0.05
            # On génère le son en partant du temps actuel
            t_vector, audio_data = self.generator.generate_note(
                self.current_freq, 
                self.current_time, 
                duration, 
                self.combo.currentText()
            )
            
            # On incrémente le temps pour le prochain bloc
            self.current_time += duration
            
            # Envoi à la carte son
            self.stream.write(audio_data)
            
            # Update visuel (on normalise t_vector pour l'affichage uniquement)
            self.curve.setData(t_vector - t_vector[0], audio_data)
            self.label_note.setText(f"Joue : {self.current_freq} Hz")
            
            QApplication.processEvents()
            
            if self.is_playing:
                self.play_loop()

    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())