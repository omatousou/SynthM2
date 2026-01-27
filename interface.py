from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg

class SynthInterface(QMainWindow):
    key_pressed = pyqtSignal(int)
    key_released = pyqtSignal(int)
    close_signal = pyqtSignal()

    def __init__(self):
        """
        1. Appelle le constructeur parent QMainWindow.
        2. Définit le titre de la fenêtre.
        3. Définit la taille de la fenêtre.
        4. Initialise l'interface utilisateur en appelant self.init_ui().
        """
        super().__init__()
        self.setWindowTitle("Synthétiseur Temps Réel")
        self.resize(800, 400)
        self.init_ui()

    def init_ui(self):
        """
        1. Crée un widget central et le définit comme widget principal de la fenêtre.
        2. Crée un layout vertical pour organiser les éléments.
        3. Crée une combo box pour choisir la forme d'onde et désactive le focus clavier dessus.
        4. Crée un label d'instructions pour l'utilisateur.
        5. Ajoute la combo box et le label au layout.
        6. Crée un widget graphique pour l'affichage du signal (oscilloscope).
        7. Ajoute ce widget au layout et crée une courbe jaune pour l'affichage du signal.
        """
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
        """
        1. Émet le signal key_pressed avec la touche pressée (event.key()).
        """
        self.key_pressed.emit(event.key())

    def keyReleaseEvent(self, event):
        """
        1. Vérifie que l'événement n'est pas une répétition automatique de la touche.
        2. Si vrai, émet le signal key_released avec la touche relâchée (event.key()).
        """
        if not event.isAutoRepeat():
            self.key_released.emit(event.key())

    def update_display(self, t, data, text):
        """
        1. Met à jour la courbe affichée avec les données temporelles t et les valeurs data.
        2. Met à jour le texte du label avec la chaîne text (fréquences ou état).
        """
        self.curve.setData(t, data)
        self.label_note.setText(text)

    def closeEvent(self, event):
        """
        1. Émet le signal close_signal pour prévenir la fermeture de l'application.
        2. Accepte l'événement de fermeture (ferme la fenêtre proprement).
        """
        self.close_signal.emit()
        event.accept()