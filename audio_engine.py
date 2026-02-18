import sounddevice as sd
import numpy as np

class AudioEngine:
    def __init__(self, fs=44100):
        """Initialise le moteur audio
        input:  - fs: Fréquence d'échantillonnage (en Hz) pour la génération du signal audio (par défaut 44100 Hz)
        
        1) Initialise la fréquence d'échantillonnage (self.fs) avec la valeur fournie
        2) Tente de créer un flux de sortie audio avec la fréquence d'échantillonnage spécifiée, 1 canal, et le type de données int16
        3) Si une erreur survient lors de l'initialisation du flux audio, affiche un message d'erreur et définit self.stream à None"""
        try:
        # 1)
            self.fs = fs
        # 2)
            self.stream = sd.OutputStream(samplerate=fs, channels=1, dtype='int16') 
            self.stream.start()
        # 3)    
        except Exception as e:
            print(f"Erreur lors de l'initialisation du flux audio : {e}")
            self.stream = None

    def play(self, data):
        """Joue le signal audio fourni
        input:  - data: Tableau de données audio à jouer (doit être un tableau numpy de type int16)

        1) Vérifie que le flux audio est actif
        2) Si le flux audio n'est pas actif, tente de le redémarrer
        3) Tente d'écrire les données audio dans le flux, en s'assurant que les données sont correctement formatées pour l'audio (int16, mono)
        4) Si une erreur survient, affiche un message d'erreur

        """
        # 1)
        if self.stream is None or not self.stream.active: # Vérifie que le flux audio est actif
        # 2)
            try:
                self.stream = sd.OutputStream(samplerate=self.fs, channels=1, dtype='int16') # Tente de redémarrer le flux audio
                self.stream.start() # Démarre le flux audio
            except Exception as e: # Si une erreur survient lors du redémarrage du flux audio
                print(f"Erreur lors du redémarrage du flux audio : {e}") # Affiche un message d'erreur
                return # Quitte la méthode si le flux audio ne peut pas être redémarré
        # 3)
        try:
            if isinstance(data, np.ndarray): # Vérifie que les données sont un tableau numpy
                data = np.asarray(data, dtype=np.int16) # Assure que les données sont de type int16 pour l'audio
                if data.ndim > 1: # Si les données ont plus d'une dimension (ex: stéréo), les convertit en mono en prenant la moyenne des canaux
                    data = data.mean(axis=1).astype(np.int16) # Convertit en mono et assure que le résultat est de type int16
                elif data.ndim == 1: # Si les données sont déjà mono, assure qu'elles sont de type int16
                    data = data.astype(np.int16)
                if data.ndim == 1: # Si les données sont mono, les reshape pour qu'elles soient compatibles avec le flux audio (shape (N, 1))
                    data = data.reshape(-1, 1) # Reshape pour mono
            self.stream.write(data) # transmet à la carte son via PortAudio, qui le joue dans les haut-parleurs.
        # 4)
        except Exception as e: # Si une erreur survient lors de la lecture des données audio
            print(f"Erreur lors de la lecture des données audio : {e}") # Affiche un message d'erreur

    def terminate(self):
        """Termine le flux audio proprement
        Vérifie si le flux audio existe, et s'il est actif, tente de le stopper et de le fermer. Si une erreur survient, affiche un message d'erreur
        """

        if self.stream is not None: # Vérifie si le flux audio existe
            try:
                self.stream.stop() # Tente de stopper le flux audio
                self.stream.close() # Tente de fermer le flux audio
            except Exception as e: # Si une erreur survient lors de la terminaison du flux audio
                print(f"Erreur lors de la terminaison du flux audio : {e}") # Affiche un message d'erreur
