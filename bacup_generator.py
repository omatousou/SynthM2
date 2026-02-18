import numpy as np

class SignalGenerator:
    def __init__(self, fs=44100):
        """
        input:  - fs: Fréquence d'échantillonnage (en Hz) pour la génération du signal audio (par défaut 44100 Hz)
        1. Initialise la fréquence d'échantillonnage (self.fs) avec la valeur fournie
        """
        self.fs = fs # Fréquence d'échantillonnage standard pour l'audio (44.1 kHz)

    def get_block(self, freqs, phases, duration, wave_type):
        """
        iput:  - freqs: Liste des fréquences à générer (en Hz)
                - phases: Dictionnaire associant chaque fréquence à une phase (en radians)
                - duration: float Durée du signal à générer (en secondes)
                - wave_type: str Type d'onde à générer ("Sinus", "Carré", "Dents de scie")
       
        output: Tuple (t, sig) où t est un tableau de temps et sig est le signal audio correspondant, normalisé et converti en int16
         
         1. Génère un signal audio de la durée spécifiée (duration) en combinant les fréquences (freqs) et les phases (phases) selon le type d'onde (wave_type)
         2. Retourne un tuple (t, sig)
        """
        # 1)
        t = np.linspace(0, duration, int(duration * self.fs), endpoint=False) # Génère un tableau de temps de 0 à duration avec un nombre d'échantillons égal à duration * fs
        sig = np.zeros_like(t) # Initialise le signal à zéro
        for freq in freqs:
            phase = phases[freq] # Récupère la phase correspondante à la fréquence actuelle
            if wave_type == "Sinus": # Si le type d'onde est "Sinus", ajoute une sinusoïde au signal
                sig += np.sin(2 * np.pi * freq * t + phase)
            elif wave_type == "Carré": # Si le type d'onde est "Carré", ajoute une onde carrée au signal
                sig += np.sign(np.sin(2 * np.pi * freq * t + phase))
            elif wave_type == "Dents de scie": # Si le type d'onde est "Dents de scie", ajoute une onde en dents de scie au signal
                sig += 2 * ((freq * t + phase / (2 * np.pi)) % 1) - 1
            else: # Si le type d'onde n'est pas reconnu, ajoute une sinusoïde par défaut
                sig += np.zeros_like(t)
        if freqs: # Si la liste des fréquences n'est pas vide, normalise le signal en divisant par le nombre de fréquences pour éviter les dépassements d'amplitude
            sig /= len(freqs) # Normalisation pour éviter les dépassements d'amplitude
        # 2)
        return t, (sig * 32767).astype(np.int16) # Convertit le signal en int16 pour l'audio (gamme de -32768 à 32767)
