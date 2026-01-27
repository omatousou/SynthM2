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
        """
        Attributs d'instance utilisés dans la classe (17) :
        self.app : QApplication principale
        self.gui : interface graphique
        self.audio : moteur audio
        self.gen : générateur de signal
        self.NOTES_MAP : dictionnaire touches/fréquences
        self.is_playing : booléen lecture en cours
        self.active_freqs : fréquences actives
        self.previous_freqs : fréquences précédentes
        self.waiting : booléen attente fin de période
        self.current_time : temps courant
        self.phase_accum : accumulateur de phase
        self.plot_buffer : buffer pour affichage
        self.timer : QTimer pour lecture par blocs
        self.wait_timer : QTimer pour attente fin de période
        self.gen.fs : fréquence d'échantillonnage (via self.gen)
        self.combo : sélection du type d'onde (via self.gui)
        self.close_signal : signal de fermeture (via self.gui)
        """
        pass

    def on_press(self, key):
        """
        Algorithme détaillé :
        1. Vérifie si la touche pressée est dans self.NOTES_MAP.
        2. Si oui, récupère la fréquence associée à la touche.
        3. Ajoute cette fréquence à self.active_freqs.
        4. Si la fréquence n'est pas déjà dans self.phase_accum :
            a. Si d'autres phases existent, synchronise la phase avec la moyenne des phases existantes.
            b. Sinon, initialise la phase à 0.
        5. Si aucune note n'était en cours de lecture et qu'il y a au moins une fréquence active :
            a. Passe self.is_playing à True.
            b. Démarre le timer pour jouer les blocs audio toutes les 25 ms.
        """
        pass

    def on_release(self, key):
        """
        Algorithme détaillé :
        1. Vérifie si la touche pressée est dans self.NOTES_MAP.
        2. Si oui, récupère la fréquence associée à la touche.
        3. Copie l'ensemble des fréquences actives dans self.previous_freqs.
        4. Retire la fréquence de self.active_freqs.
        5. Si plus aucune fréquence n'est active :
            a. Passe self.is_playing à False et self.waiting à True.
            b. Calcule la période d'attente (LCM des périodes des fréquences précédentes).
            c. Crée un QTimer (self.wait_timer) pour attendre la fin de la période.
        6. Sinon, si d'autres notes restent actives :
            a. Met à jour l'affichage du signal restant sur l'interface.
        """
        pass

    def play_block(self):
        """
        Algorithme détaillé :
        1. Vérifie si self.is_playing ou self.waiting est vrai.
        2. Si oui, crée la liste freqs (self.previous_freqs si waiting, sinon self.active_freqs).
        3. Si freqs n'est pas vide :
            a. Définit duration à 0.05.
            b. Crée le dictionnaire phases pour chaque fréquence.
            c. Appelle self.gen.get_block pour générer le signal audio.
            d. Met à jour la phase de chaque fréquence dans self.phase_accum.
            e. Incrémente self.current_time de duration.
            f. Joue le bloc audio avec self.audio.play.
            g. Ajoute les données audio à self.plot_buffer.
            h. Si self.plot_buffer dépasse la taille max, ne garde que les derniers échantillons.
            i. Crée t_plot pour l'affichage.
            j. Met à jour l'affichage graphique avec les fréquences jouées.
        """
        pass

    def end_wait(self):
        """
        Algorithme détaillé :
        1. Passe self.waiting à False.
        2. Arrête le timer de lecture (self.timer.stop()).
        3. Vide self.plot_buffer.
        4. Met à jour l'affichage graphique pour indiquer l'état de repos (self.gui.update_display).
        """
        pass

    def on_close(self):
        """
        Algorithme détaillé :
        1. Appelle self.audio.terminate() pour libérer les ressources audio lors de la fermeture de l'application.
        """
        pass

    def run(self):
        """
        Algorithme détaillé :
        1. Affiche l'interface graphique (self.gui.show()).
        2. Démarre la boucle principale Qt (sys.exit(self.app.exec_())).
        """
        pass

if __name__ == "__main__":
    ctrl = AppController()
    ctrl.run()