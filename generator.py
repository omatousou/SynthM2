import numpy as np

class SignalGenerator:
    def __init__(self, fs=44100):
        """
        Algorithme détaillé :
        1. Initialise la fréquence d'échantillonnage (self.fs) avec la valeur fournie (par défaut 44100 Hz).
        """
        self.fs = fs

    def get_block(self, freqs, phases, duration, wave_type):
        """
        Algorithme détaillé :
        1. Crée un vecteur temps t allant de 0 à duration avec un pas adapté à la fréquence d'échantillonnage.
        2. Initialise le signal sig à un tableau de zéros de la même taille que t.
        3. Pour chaque fréquence dans freqs :
            a. Récupère la phase initiale associée à la fréquence.
            b. Selon le type d'onde demandé (wave_type) :
                - "Sinus" : additionne une sinusoïde à sig.
                - "Carré" : additionne un signal carré à sig.
                - "Dents de scie" : additionne une onde en dents de scie à sig.
                - Autre : additionne un tableau de zéros (aucun signal).
        4. Si la liste des fréquences n'est pas vide, divise sig par le nombre de fréquences (normalisation pour éviter la saturation).
        5. Retourne le vecteur temps t et le signal sig converti en int16 et mis à l'échelle pour l'audio.
        """
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
        if freqs:
            sig /= len(freqs)
        return t, (sig * 0.2 * 32767).astype(np.int16)