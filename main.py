
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

        ## ATTRIBUTS :
        self.app = QApplication(sys.argv) # Application Qt. sys.argv : argument vector est la liste des paramètres envoyés au programme lors de son lancement. Ici contient le chemin vers le fichier Python.
                                          # Exemple : python mon_jeu.py --fullscreen --level 5 ALORS sys.argv[0] : "mon_jeu.py" sys.argv[1] : "--fullscreen" sys.argv[2] : "--level"sys.argv[3] : "5"
        self.gui = SynthInterface() # Import de la classe SynthInterface dans le fichier interface.py
        self.audio = AudioEngine() # Import de la classe AudioEngine dans le fichier audio_engine.py
        self.gen = SignalGenerator() # Import de la classe SignalGenerator dans le fichier generator.py


        # f = 440 * (2 ** ((n - 69) / 12)):  convention MIDI, où la note 69 correspond au La4 (440 Hz). http://antoinegabrielbrun.com/ressources/frequence-des-notes-de-la-gamme/
        calc_freq = lambda n: round(440 * (2 ** ((n - 69) / 12)), 2)

        # Touche Midi : Frequences associées

        self.NOTES_MAP = {
            # Touches Blanches
            Qt.Key_Q: calc_freq(60),  # Do (C4)
            Qt.Key_S: calc_freq(62),  # Ré
            Qt.Key_D: calc_freq(64),  # Mi
            Qt.Key_F: calc_freq(65),  # Fa
            Qt.Key_G: calc_freq(67),  # Sol
            Qt.Key_H: calc_freq(69),  # La
            Qt.Key_J: calc_freq(71),  # Si
            Qt.Key_K: calc_freq(72),  # Do (C5)
            Qt.Key_L: calc_freq(74),  # Ré

            # Touches Noires
            Qt.Key_Z: calc_freq(61),  # Do#
            Qt.Key_E: calc_freq(63),  # Ré#
            Qt.Key_T: calc_freq(66),  # Fa#
            Qt.Key_Y: calc_freq(68),  # Sol#
            Qt.Key_U: calc_freq(70),  # La#
            Qt.Key_O: calc_freq(73),  # Do#
            Qt.Key_P: calc_freq(75),  # Ré#
}


        self.is_playing = False # Indique si une note est en cours de lecture
        self.active_freqs = set() # Fréquences actuellement jouées. Utilisation d'un set pour éviter les doublons
        self.previous_freqs = set() # Fréquences jouées avant l'arrêt. Utilisation d'un set pour éviter les doublons
        self.waiting = False # Indique si on est en période d'attente avant d'arrêter le son
        self.current_time = 0.0 # Temps courant en secondes
        self.phase_accum = {}  # Accumulateur de phase pour chaque fréquence
        self.plot_buffer = []  # Buffer pour l'affichage graphique

        # Configure une alarme qui déclenchera la fonction "play_block" à chaque fois que le délai sera écoulé.
        self.timer = QTimer() #in
        self.timer.timeout.connect(self.play_block) # timeout signale émis lorsque le délai est écoulé (délai défini par start) et appelle play_block. Le lien est fait via la méthode connect.

        # Connexion des signaux de l'interface
        # Connecte les événements d'entrée (clavier et fermeture) aux fonctions de gestion correspondantes.
        self.gui.key_pressed.connect(self.on_press) # Si une touche est pressée, appelle on_press. Le lien est fait via la méthode connect.
        self.gui.key_released.connect(self.on_release) # Si une touche est relâchée, appelle on_release. Le lien est fait via la méthode connect.
        self.gui.close_signal.connect(self.on_close) # Si la fenêtre est fermée, appelle on_close. Le lien est fait via la méthode connect.

    def on_press(self, key):
        """
        1. Récupère et vérifie si la touche pressée est dans self.NOTES_MAP.
        2. Si oui, récupère la fréquence associée à la touche.
        3. Ajoute cette fréquence à self.active_freqs.
        4. Si la fréquence n'est pas déjà dans self.phase_accum :
            a. Si d'autres phases existent, synchronise la phase avec la moyenne des phases existantes.
            b. Sinon, initialise la phase à 0.
        5. Si aucune note n'était en cours de lecture et qu'il y a au moins une fréquence active :
            a. Passe self.is_playing à True.
            b. Démarre le timer pour jouer les blocs audio toutes les 25 ms.
        """
        key_freq = self.NOTES_MAP.get(key) # Récupère la fréquence associée à la touche pressée
        if key_freq: # Si la touche est dans self.NOTES_MAP
            self.active_freqs.add(key_freq) # Ajoute la fréquence à l'ensemble des fréquences actives
            # Pour eviter les glitches, on synchronise la phase des nouvelles notes avec la moyenne des phases existantes
            if key_freq not in self.phase_accum: # Si la fréquence n'a pas encore de phase accumulée
                if self.phase_accum: # S'il y a déjà des phases accumulées
                    avg_phase = np.mean(list(self.phase_accum.values())) # Calcule la moyenne des phases existantes
                    self.phase_accum[key_freq] = avg_phase # Initialise la phase de la nouvelle fréquence avec la moyenne
                else:
                    self.phase_accum[key_freq] = 0.0 # Sinon, initialise la phase à 0

            if not self.is_playing and self.active_freqs: # Si aucune note n'était en cours de lecture et qu'il y a au moins une fréquence active
                self.is_playing = True # Passe is_playing à True
                self.timer.start(25)  # Joue les blocs audio toutes les 25 ms

    def on_release(self, key):
        """

        1. Vérifie si la touche pressée est dans self.NOTES_MAP.
        2. Si oui, récupère la fréquence associée à la touche.
        3. Copie l'ensemble des fréquences actives dans self.previous_freqs.
        4. Retire la fréquence de self.active_freqs.
        5. Si plus aucune fréquence n'est active :
            a. Passe self.is_playing à False et self.waiting à True.
            b. Calcule la période d'attente (PGCD (LCM) des périodes des fréquences précédentes).
            c. Crée un QTimer (self.wait_timer) pour attendre la fin de la période.
        6. Sinon, si d'autres notes restent actives :
            a. Met à jour l'affichage du signal restant sur l'interface.
        """
        key_freq = self.NOTES_MAP.get(key) # Récupère la fréquence associée à la touche pressée
        if key_freq: # Si la touche est dans self.NOTES_MAP
            self.previous_freqs = self.active_freqs.copy() # Copie l'ensemble des fréquences actives dans self.previous_freqs
            self.active_freqs.remove(key_freq) # Retire la fréquence de l'ensemble des fréquences actives
            if not self.active_freqs: # Si plus aucune fréquence n'est active
                self.is_playing = False # Passe is_playing à False
                self.waiting = True # Passe waiting à True

                self.wait_timer = QTimer() # Crée un QTimer pour gérer la période d'attente
                # Calcul de la période d'attente comme le PPCM des périodes des fréquences précédentes  
                periods = [Fraction(1, f).limit_denominator(1000) for f in self.previous_freqs] # Liste des périodes sous forme de fractions les plus simples maximum 1/1000
                wait_time = np.lcm(periods)
                self.wait_timer = QTimer()
                self.wait_timer.setSingleShot(True)
                self.wait_timer.timeout.connect(self.end_wait)
                self.wait_timer.start(int(wait_time * 1000))
            elif self.is_playing:
                # Met à jour l'affichage du signal restant
                duration = 0.025 # Durée de 25 ms pour l'affichage
                t = np.linspace(0, duration, int(duration * self.gen.fs), endpoint=False) # Vecteur temps
                sig = self.gen.get_block(list(self.active_freqs), self.phase_accum, duration, self.gui.get_wave_type()) # Génère le signal audio correspondant aux fréquences restantes à jouer pour l'affichage graphique
                self.gui.update_display(t, sig, list(self.active_freqs)) # Met à jour l'affichage graphique avec les fréquences restantes et le signal audio correspondant


    def play_block(self):
        if self.is_playing or self.waiting: # Si on est en train de jouer ou en période d'attente
            if self.waiting: # Si on est en période d'attente, on joue les fréquences précédentes pour faire une queue de résonance
                freqs = self.previous_freqs # Utilise les fréquences précédentes pour continuer à jouer le son pendant la période d'attente
            else: # Sinon, on joue les fréquences actives
                freqs = self.active_freqs # Utilise les fréquences actives pour jouer le son
        if freqs : 
            duration = 0.05 # Durée de 50 ms pour le bloc audio
            phases = {f: self.phase_accum.get(f, 0) for f in freqs} # Dictionnaire des phases pour chaque fréquence soit la phase accumulée, soit 0 si elle n'existe pas
            t, block = self.gen.get_block(list(freqs), phases, duration, self.gui.get_wave_type()) # Génère le bloc audio avec les fréquences, les phases, la durée et le type d'onde sélectionné dans l'interface. 
            #Appelle la méthode get_block de la classe SignalGenerator (via l’instance self.gen) pour obtenir le signal audio à jouer. Les arguments sont :
            # list(freqs) : la liste des fréquences à jouer (convertie en liste à partir de l'ensemble freqs)
            # phases : le dictionnaire des phases pour chaque fréquence
            # duration : la durée du bloc audio à générer (0.05 secondes)
            # self.gui.get_wave_type() : le type d'onde sélectionné dans l'interface graphique (Sinus, Carré ou Dents de scie)  
            for f in freqs:
                self.phase_accum[f] = (phases[f] + 2 * np.pi * f * duration) % (2 * np.pi) # Incrémente de duration à la phase de chaque fréquence (en radians), puis ramène la phase dans [0, 2π[ pour garantir la continuité périodique du signal
            self.current_time += duration # Incrémente le temps courant de 0.05 s à chaque bloc audio (correspond à la durée du bloc)
            self.audio.play(block) # Joue le bloc audio avec la méthode play de la classe AudioEngine (via l’instance self.audio). Le bloc audio est un tableau de samples converti en int16 et mis à l'échelle pour l'audio.
            self.plot_buffer.extend(block) # Ajoute les données audio au buffer d'affichage pour pouvoir les afficher graphiquement dans l'interface
            if len(self.plot_buffer) > self.gen.fs: # Si le buffer dépasse la taille maximale (1 seconde d'audio)
                self.plot_buffer = self.plot_buffer[-self.gen.fs:] # Ne garde que les derniers échantillons pour l'affichage (correspond à 1 seconde d'audio)
            t_plot = np.linspace(0, len(self.plot_buffer) / self.gen.fs, len(self.plot_buffer), endpoint=False) # Vecteur temps pour l'affichage correspondant à la taille du buffer d'affichage
            self.gui.update_display(t_plot, self.plot_buffer, list(freqs)) # Met à jour l'affichage graphique avec les fréquences jouées et le signal audio correspondant. Les arguments sont :
            # t_plot : le vecteur temps pour l'affichage graphique
            # self.plot_buffer : le signal audio à afficher graphiquement (correspond au buffer d'affichage)
            # list(freqs) : la liste des fréquences actuellement jouées (convertie en liste à partir de l'ensemble freqs) pour afficher les fréquences jouées dans l'interface.


    def end_wait(self):
        self.waiting = False # Passe waiting à False pour indiquer que la période d'attente est terminée
        self.timer.stop() # Arrête le timer de lecture pour ne plus jouer de blocs audio
        self.plot_buffer = [] # Vide le buffer d'affichage pour ne plus afficher de signal
        self.gui.update_display([], [], "Repos") # Met à jour l'affichage graphique pour indiquer l'état de repos (aucune fréquence, aucun signal, texte "Repos")  
        """
        1. Passe self.waiting à False.
        2. Arrête le timer de lecture (self.timer.stop()).
        3. Vide self.plot_buffer.
        4. Met à jour l'affichage graphique pour indiquer l'état de repos (self.gui.update_display).
        """

    def on_close(self):
        """

        1. Appelle self.audio.terminate() pour libérer les ressources audio lors de la fermeture de l'application.
        """
        self.audio.terminate() # Appelle la méthode terminate de la classe AudioEngine (via l’instance self.audio) pour libérer les ressources audio utilisées par l'application lors de sa fermeture.
        pass

        

    def run(self):
        self.gui.show() # Affiche l'interface graphique en appelant la méthode show de la classe SynthInterface (via l’instance self.gui)
        sys.exit(self.app.exec_()) # Démarre la boucle principale de l'application Qt en appelant la méthode exec_ de l'instance self.app. sys.exit est utilisé pour s'assurer que le programme se termine proprement lorsque la boucle Qt est terminée (lorsque la fenêtre est fermée).

        pass

if __name__ == "__main__":
    ctrl = AppController()
    ctrl.run()
