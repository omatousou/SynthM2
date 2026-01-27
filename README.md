# Documentation des Modules - Synthétiseur Temps Réel

Ce projet est un synthétiseur audio temps réel développé en Python. Il est composé de 4 modules principaux qui travaillent ensemble pour générer et jouer du son en direct.

---

## 📋 Table des Matières

1. [audio_engine.py](#audio_enginepy)
2. [generator.py](#generatorpy)
3. [interface.py](#interfacepy)
4. [plot_curve.py](#plot_curvepy)

---

## 🔊 audio_engine.py

### Description
Module responsable de la gestion de la lecture audio en temps réel. Il utilise la bibliothèque `sounddevice` pour contrôler le périphérique audio du système.

### Classe : `AudioEngine`

#### Méthodes

- **`__init__(fs=44100)`**
  - Initialise le moteur audio
  - Paramètre `fs` : fréquence d'échantillonnage en Hz (par défaut 44100 Hz)
  - Crée un flux de sortie audio (OutputStream)

- **`play(data)`**
  - Joue les données audio fournies
  - Paramètre `data` : tableau numpy contenant les échantillons audio

- **`terminate()`**
  - Arrête le flux audio et ferme la connexion au périphérique audio
  - À appeler lors de l'arrêt de l'application

```python
engine = AudioEngine(fs=44100)
engine.play(audio_data)
engine.terminate()
```

---

## 🎵 generator.py

Module de génération de signaux audio. Il produit différentes formes d'ondes (sinusoïdale, carrée, dent de scie) avec support des phases et fréquences multiples.

### Classe : `SignalGenerator`


- **`__init__(fs=44100)`**
  - Initialise le générateur de signal

- **`get_block(freqs, phases, duration, wave_type)`**
  - Génère un bloc de signal audio
  - Paramètres :
    - `freqs` : liste des fréquences à générer
    - `phases` : dictionnaire des phases pour chaque fréquence
    - `duration` : durée du bloc en secondes
    - `wave_type` : type d'onde ("Sinus", "Carré", "Dents de scie")
  - Retourne : tuple (t, audio_data)
    - `t` : vecteur temps

### Formes d'ondes supportées

- **Sinus** : sin(2πft + phase)
- **Carré** : sign(sin(2πft + phase))
- **Dents de scie** : 2 × ((ft + phase/(2π)) mod 1) - 1

### Exemple d'utilisation
```python
gen = SignalGenerator(fs=44100)
phases = {440: 0, 880: 0}
```
---
## 🎹 interface.py
### Description


#### Signaux (Signals)
- **`key_pressed`** : Émis lors de la pression d'une touche
- **`key_released`** : Émis lors du relâchement d'une touche
- **`close_signal`** : Émis lors de la fermeture de la fenêtre

#### Méthodes

- **`__init__()`**
  - Initialise l'interface
  - Crée la fenêtre principale (800x400)

- **`init_ui()`**
  - Configure l'interface utilisateur
  - Ajoute :
    - Sélecteur de type d'onde (ComboBox)
    - Label d'instructions
    - Graphique de visualisation en temps réel

- **`keyPressEvent(event)`**
  - Gère les pressions de touches
  - Émet le signal `key_pressed`

- **`keyReleaseEvent(event)`**
  - Gère les relâchements de touches
  - Émet le signal `key_released`

- **`update_display(t, data, text)`**
  - Met à jour le graphique et le label d'affichage
  - Paramètres :
    - `t` : vecteur temps
    - `data` : données audio à afficher
    - `text` : texte à afficher (note jouée)

### Touches clavier

| Touche | Fréquence | Note |
|--------|-----------|------|
| A | 261.63 Hz | Do4 |
| Z | 293.66 Hz | Ré4 |
| E | 329.63 Hz | Mi4 |
| R | 349.23 Hz | Fa4 |
| T | 392.00 Hz | Sol4 |
| Y | 440.00 Hz | La4 |
| U | 493.88 Hz | Si4 |

### Exemple d'utilisation
```python
app = QApplication(sys.argv)
interface = SynthInterface()
interface.show()
sys.exit(app.exec_())
```

---

## 📊 plot_curve.py

### Description
Application complète combinant tous les modules. C'est le point d'entrée principal du synthétiseur qui intègre la génération de signal, l'audio engine et l'interface graphique avec continuité de phase pour éviter les glitchs.

### Classe : `SignalGenerator` (version locale)

Génère des notes avec continuité de phase pour une lecture sans interruption.

- **`generate_note(freq, start_time, duration, wave_type, fs)`**
  - Génère une note individuelle
  - Utilise `start_time` pour maintenir la continuité de phase
  - Retourne : (t, audio_data)

### Classe : `MainWindow`

Fenêtre principale du synthétiseur.

#### Attributs importants

- `stream` : flux audio sounddevice
- `NOTES_MAP` : dictionnaire mappant les touches clavier aux fréquences
- `current_time` : variable cruciale pour la continuité de phase

#### Fonctionnalités

- Lecture temps réel sans glitchs
- Affichage graphique de l'onde
- Sélection du type d'onde (Sinus, Carré, Dents de scie)
- Clavier AZERTY pour jouer des notes

### Exemple d'utilisation (ligne de commande)
```bash
python plot_curve.py
```

---

## 🚀 Installation des dépendances

```bash
pip install numpy sounddevice PyQt5 pyqtgraph
```

### Dépendances requises
- **numpy** : Manipulation de tableaux et calculs mathématiques
- **sounddevice** : Gestion de l'audio
- **PyQt5** : Interface graphique
- **pyqtgraph** : Visualisation en temps réel

---

## 🎯 Architecture générale

```
plot_curve.py (Application principale)
    ├── SignalGenerator (generator.py)
    │   └── Génère les formes d'ondes
    ├── AudioEngine (audio_engine.py)
    │   └── Joue le son
    └── SynthInterface (interface.py)
        └── Affiche l'interface et gère l'entrée utilisateur
```

---

## 💡 Notes importantes

1. **Continuité de phase** : `plot_curve.py` maintient une continuité de phase pour éviter les clics et pops lors du changement de notes.

2. **Fréquence d'échantillonnage** : Par défaut 44100 Hz (qualité CD)

3. **Normalisation** : Le signal est normalisé pour éviter l'écrêtage (clipping)

4. **Réactivité** : Utilise un blocksize de 1024 pour une bonne réactivité tout en minimisant les glitchs

---

## 📝 Auteur
Projet de synthétiseur audio temps réel en Python

## 📄 Licence
À définir selon vos besoins
