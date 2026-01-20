from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg

class SynthInterface(QMainWindow):
    key_pressed = pyqtSignal(int)
    key_released = pyqtSignal(int)
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synthétiseur Temps Réel")
        self.resize(800, 400)

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
        self.key_pressed.emit(event.key())

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.key_released.emit(event.key())

    def update_display(self, t, data, text):
        self.curve.setData(t, data)
        self.label_note.setText(text)

    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()