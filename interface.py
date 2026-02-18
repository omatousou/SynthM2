from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg

class SynthInterface(QMainWindow):
    """Interface graphique du synthétiseur
    - Affiche un oscilloscope temps réel du signal généré
    - Affiche un clavier visuel qui s'illumine quand on appuie sur les touches
    - Permet de choisir la forme d'onde (sinus, carré, dents de scie)
    
    Initialisation de pyqtSignal pour les événements de touche et de fermeture de la fenêtre
    """
    key_pressed = pyqtSignal(int)
    key_released = pyqtSignal(int)
    close_signal = pyqtSignal()

    def __init__(self):
        """
        1 ) Appelle le constructeur parent QMainWindow pour initialiser la fenêtre
        2 ) Définit le titre de la fenêtre à <<Synthétiseur>>
        3 ) Définit la taille de la fenêtre à 900x500 pixels
        4 ) Création des attributs pour les éléments de l'interface
        5 ) Initialise les éléments de l'interface utilisateur en appelant self.init_ui()

        Attributs :
        - self.key_buttons : Dictionnaire pour stocker les boutons du clavier visuel
        - self.mode_selection : QComboBox pour la sélection de la forme d'onde
        - self.oscilloscope : Widget graphique pour l'affichage du signal (oscilloscope)
        - self.oscilloscope_screen : Plot pyqtgraph pour dessiner le signal
        - self.signal : Courbe du signal dans le plot
        - self.white_keys : Liste des touches blanches du clavier
        - self.black_keys : Liste des touches noires du clavier
        - self.keyboard : Référence à self pour l'accès simple aux méthodes de mise à jour du clavier

        """
        # 1)
        super().__init__() # Appel du constructeur parent pour initialiser la fenêtre

        # 2)
        self.setWindowTitle("Synthétiseur") # Définition du titre de la fenêtre

        # 3)
        self.resize(900, 500) # Définition de la taille de la fenêtre

        # 4)
        # Attributs
        self.key_buttons = {}           # Dictionnaire des boutons
        self.mode_selection = None      # Sélecteur de forme d'onde
        self.oscilloscope = None        # Widget graphique pour l'affichage du signal (oscilloscope)
        self.oscilloscope_screen = None # Plot pyqtgraph pour dessiner le signal
        self.signal = None              # Courbe du signal
        # Clavier MIDI
        self.white_keys = ["Q", "Z", "S", "E", "D", "F", "T", "G", "Y", "H", "U", "J", "K", "O", "L", "P"]
        self.black_keys = ["Z", "E", "T", "Y", "U", "O", "P"]
        self.keyboard = self  # Référence à self pour l'accès simple aux méthodes de mise à jour du clavier

        # 5)
        self.init_ui() # Initialisation de l'interface utilisateur

    def init_ui(self):
        """Initialise les éléments de l'interface utilisateur
        1. Crée un widget central et le définit comme widget principal de la fenêtre
        2. Crée un agencement vertical pour organiser les éléments
        3. Crée des boutons pour choisir la forme d'onde et les ajoute à l'agencement
        4. Crée un widget graphique pour l'affichage du signal (oscilloscope) et l'ajoute à l'agencement
        5. Crée un signal jaune pour l'affichage du signal dans l'oscilloscopes sur l'oscilloscope_screen
        6. Crée un widget clavier pour afficher les touches actives et l'ajoute à l'agencement
        """
        # 1) Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 2) Agencement vertical principal
        main_layout = QVBoxLayout(central_widget)

        # 3) Choix de la forme d'onde
        self.mode_selection = QComboBox() # Création d'un menu déroulant pour choisir la forme d'onde
        self.mode_selection.addItems(["Sinus", "Carré", "Dents de scie"]) # Ajout des options de forme d'onde
        self.mode_selection.setFocusPolicy(Qt.NoFocus) # Pour que le clavier puisse être utilisé pour jouer du piano sans que le menu prenne le focus
        main_layout.addWidget(QLabel("Forme d'onde :")) # Ajout d'un label pour indiquer la fonction du menu déroulant
        main_layout.addWidget(self.mode_selection) # Ajout du menu déroulant à l'agencement principal

        # 4) Oscilloscope
        self.oscilloscope = pg.GraphicsLayoutWidget() # Widget pour contenir l'affichage de l'oscilloscope
        main_layout.addWidget(self.oscilloscope) # Ajouter le widget à l'agencement principal
        # Configuration de l'ecran de l'oscilloscope
        self.oscilloscope_screen = self.oscilloscope.addPlot() # Ajouter un affichage à l'oscilloscope
        self.oscilloscope_screen.hideAxis('left')   # Masquer l'axe Y sur l'affichage de l'oscilloscope
        self.oscilloscope_screen.hideAxis('bottom')  # Masquer l'axe X sur l'affichage de l'oscilloscope
        self.signal = self.oscilloscope_screen.plot(pen='y') # Créer une courbe jaune pour l'affichage du signal dans l'oscilloscope_screen
        # On fixe l'échelle verticale pour éviter que ça déborde de trop
        # Amplitude originale * facteur d'échelle pour avoir de l'espace autour du signal
        amplitude = 32767  # Amplitude max pour un signal int16
        scale_factor = 1.2  # 20% d'espace supplémentaire
        self.oscilloscope_screen.setYRange(-amplitude * scale_factor, amplitude * scale_factor) # Fixer les limites de l'amplitude du signal dans l'affichage de l'oscilloscope

        # 5 ) Clavier visuel
        keys_layout = QHBoxLayout()
        keys_layout.setSpacing(2)  # Espace très fin entre les touches
        

        for note in self.white_keys: # On crée un bouton pour chaque note
            btn = QPushButton(note) # Le texte du bouton est la note (ex: "Q")
            btn.setEnabled(False) # On désactive les boutons pour qu'ils ne soient pas cliquables
            btn.setFixedWidth(50)  # Même taille pour tout le monde
            
            # Définition du style selon si c'est une noire ou une blanche
            if note in self.black_keys:
                style = "background-color: black; color: white; border: 1px solid gray; height: 100px; font-weight: bold;"
            else:
                style = "background-color: white; color: black; border: 1px solid black; height: 100px; font-weight: bold;"
            # On applique le style au bouton
            btn.setStyleSheet(style)
            
            btn.setProperty("original_style", style)# On enregistre son style "normal" dans une propriété personnalisée
            self.key_buttons[note] = btn # On stocke le bouton dans le dictionnaire avec la note comme clé (ex: "Q": <QPushButton>)
            keys_layout.addWidget(btn) # On ajoute le bouton à l'agencement des touches
        
        main_layout.addLayout(keys_layout) # On ajoute l'agencement des touches à l'agencement principal
        
        # self.keyboard pointe vers self pour l'accès simple: self.gui.keyboard.set_key_active()
        self.keyboard = self

    def get_wave_type(self):
        """Méthode pour que le 'Main' puisse savoir quelle onde est choisie"""
        return self.mode_selection.currentText()

    def update_visual_key(self, key_code, pressed=True):
        """
        Change la couleur de la touche et la remet à l'état initial
        1. Récupère le nom de la touche à partir du code de la touche (key_code) en utilisant chr() et en convertissant en majuscule
        2. Vérifie si le nom de la touche existe dans le dictionnaire des boutons du clavier (self.key_buttons)
        3. Si la touche est trouvée, récupère le bouton correspondant
        4. Si pressed est True, change le style du bouton pour indiquer qu'il est actif (par exemple, en le colorant en orange)
        5. Si pressed est False, récupère le style original du bouton à partir de la propriété "original_style" et le réapplique pour indiquer que la touche est relâchée
        
        """
        # 1)
        if 0 <= key_code <= 255: # Vérifie que le code de la touche est dans la plage des caractères ASCII
            char = chr(key_code).upper() # Convertit le code de la touche en caractère et le met en majuscule
        else:
            char = None # Si le code de la touche n'est pas valide, on met char à None  

        # 2)
        if char in self.key_buttons: # Vérifie si le nom de la touche existe dans le dictionnaire des boutons du clavier
        # 3)
            btn = self.key_buttons[char] # Récupère le bouton correspondant à la touche
        # 4)
            if pressed:
                # Quand on appuie : elle devient orange
                btn.setStyleSheet("background-color: orange; color: black; border: 1px solid black; height: 100px; font-weight: bold;")
            else:
                # Quand on relâche : on récupère le style qu'on avait stocké au début !
                original = btn.property("original_style")
                btn.setStyleSheet(original)

    def set_key_active(self, key_code, is_active):
        """Méthode appelée par main.py via self.gui.keyboard.set_key_active()"""
        self.update_visual_key(key_code, is_active)

    def keyPressEvent(self, event):
        """Gère les événements de pression de touche
        1. Vérifie que l'événement n'est pas une répétition automatique de la touche
        2. Si vrai, met à jour la touche visuelle correspondante en appelant self.update_visual_key() avec pressed=True
        3. Émet le signal key_pressed avec la touche pressée (event.key())
        """
        if not event.isAutoRepeat(): # 1)
            self.update_visual_key(event.key(), True) # 2) L'argument pressed=True pour indiquer que la touche est pressée
            self.key_pressed.emit(event.key()) # 3)

    def keyReleaseEvent(self, event):
        """Gère les événements de relâchement de touche
        1. Vérifie que l'événement n'est pas une répétition automatique de la touche
        2. Si vrai, met à jour la touche visuelle correspondante en appelant self.update_visual_key() avec pressed=False
        3. Émet le signal key_released avec la touche relâchée (event.key())
        """
        if not event.isAutoRepeat(): # 1)
            self.update_visual_key(event.key(), False)  # 2) L'argument pressed=False pour indiquer que la touche est relâchée
            self.key_released.emit(event.key()) # 3

    def update_display(self, t, data):
        """
        1. Met à jour la courbe affichée avec les données temporelles t et les valeurs data en appelant self.signal.setData(t, data)
        """
        self.signal.setData(t, data) # 1)


    def closeEvent(self, event):
        """
        1. Émet le signal close_signal pour prévenir la fermeture de l'application.
        2. Accepte l'événement de fermeture (ferme la fenêtre proprement).
        """
        # 1) 
        self.close_signal.emit()
        # 2)
        event.accept()
        
