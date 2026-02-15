# SynthM2 - Synthétiseur Audio Temps Réel

Un synthétiseur audio temps réel développé en Python avec interface graphique PyQt5. Jouez des notes en utilisant votre clavier et visualisez les ondes générées en temps réel.

---

## 📋 Table des Matières

1. [Installation](#installation)
2. [Démarrage rapide](#démarrage-rapide)
3. [Architecture](#architecture)
4. [Modules](#modules)
5. [Contrôles clavier](#contrôles-clavier)
6. [Fonctionnalités](#fonctionnalités)

---

## � Installation

### Prérequis
- Python 3.7+
- pip ou conda

### Installez les dépendances

```bash
pip install numpy sounddevice PyQt5 pyqtgraph
```

### Dépendances requises
| Paquet | Version | Utilité |
|--------|---------|---------|
| **numpy** | ≥1.20 | Calculs mathématiques et manipulation de tableaux |
| **sounddevice** | ≥0.4.5 | Gestion de l'audio et sortie audio |
| **PyQt5** | ≥5.15 | Interface graphique |
| **pyqtgraph** | ≥0.12 | Visualisation en temps réel des ondes |

---

## ⚡ Démarrage Rapide

```bash
python main.py
```

L'application affichera une fenêtre avec un clavier virtuel et un oscilloscope en temps réel.

---

## 🏗 Architecture

Le projet utilise une architecture modulaire avec une classe `App` principale qui orchestre :

```
main.py (Point d'entrée)
    └── App (Gération complète de l'application)
        ├── SynthInterface (interface.py)
        │   └── Interface PyQt5 avec clavier et oscilloscope
        ├── AudioEngine (audio_engine.py)
        │   └── Gestion de la sortie audio
        ├── SignalGenerator (generator.py)
        │   └── Génération des formes d'ondes
        └── Timers Qt
            ├── timer (25ms) - Génération des blocs audio
            └── release_timer (10ms) - Fade-out après relâchement
```

---

## 📚 Modules

### 🔊 audio_engine.py

Module responsable de la gestion de la lecture audio en temps réel via `sounddevice`.

#### Classe : `AudioEngine`

| Méthode | Description |
|---------|-------------|
| `__init__(fs=44100)` | Initialise le moteur audio avec la fréquence d'échantillonnage (44.1 kHz par défaut) |
| `play(data)` | Joue les données audio fournies (tableau numpy) |
| `terminate()` | Arrête le flux audio et ferme la connexion au périphérique |

### 🎵 generator.py

Module de génération de signaux audio support des formes d'ondes multiples.

#### Classe : `SignalGenerator`

| Méthode | Description |
|---------|-------------|
| `__init__(fs=44100)` | Initialise le générateur de signal |
| `get_block(freqs, phases, duration, wave_type)` | Génère un bloc audio de la durée spécifiée |

#### Formes d'ondes supportées

- **Sinus** : $\sin(2\pi ft + \phi)$
- **Carré** : $\text{sign}(\sin(2\pi ft + \phi))$
- **Dents de scie** : $2 \cdot ((ft + \phi/(2\pi)) \bmod 1) - 1$
- **Triangle** : Disponible selon l'implémentation

où :
- $f$ = fréquence (Hz)
- $t$ = temps (s)
- $\phi$ = phase (radians)

### 🎹 interface.py

Module de l'interface utilisateur PyQt5. Fournit le clavier virtuel et la visualisation en temps réel.

#### Classe : `SynthInterface`

| Méthode | Description |
|---------|-------------|
| `__init__()` | Initialise l'interface (800x400 px) |
| `init_ui()` | Configure les éléments UI (clavier, oscilloscope, sélecteur d'onde) |
| `keyPressEvent(event)` | Gère les pressions de touches, émet `key_pressed` |
| `keyReleaseEvent(event)` | Gère les relâchements de touches, émet `key_released` |
| `update_display(t, data)` | Met à jour le graphique en temps réel |
| `get_wave_type()` | Retourne le type d'onde sélectionnée |

#### Signaux (PyQt5 Signals)
- **`key_pressed`** : Émis lors de la pression d'une touche
- **`key_released`** : Émis lors du relâchement d'une touche
- **`close_signal`** : Émis lors de la fermeture de la fenêtre

### 🎚 main.py

Fichier principal qui contient la classe `App` orchestrant toute l'application.

#### Classe : `App`

Gère l'orchestration complète du synthétiseur :

| Feature | Description |
|---------|-------------|
| **Gestion des notes** | Détection des touches et gestion des fréquences actives |
| **Continuité de phase** | Maintien des accumulateurs de phase pour éviter les clics |
| **Polyphonie** | Support de notes multiples simultanées |
| **Fade-out** | Période d'attente de 10ms après relâchement pour une résonance naturelle |
| **Visualisation** | Oscilloscope en temps réel affichant 30ms de données |
| **Timers** | Timer de 25ms pour la génération de blocs audio |

#### Attributs principaux

```python
self.active_freqs      # Set des fréquences actuellement jouées
self.phase_accum       # Dict des phases accumulées par fréquence
self.plot_buffer       # Buffer d'affichage pour l'oscilloscope
self.current_time      # Temps courant en secondes
self.is_playing        # État de lecture
self.waiting           # État d'attente post-relâchement
```

#### Callbacks principaux

| Callback | Déclencheur | Fonction |
|----------|-------------|----------|
| `key_pressed_callback(key)` | Pression de touche | Ajoute fréquence, démarre timer |
| `key_released_callback(key)` | Relâchement de touche | Supprime fréquence, lance fade-out |
| `end_timer_callback()` | Timer (25ms) | Génère et joue un bloc audio |
| `end_play_callback()` | Timer relâchement (10ms) | Arrête complètement l'audio |
| `close_callback()` | Fermeture fenêtre | Libère ressources audio |

---

## ⌨️ Contrôles Clavier

#### Touches Blanches (Notes naturelles)

| Touche | Fréquence | Note | Octave |
|--------|-----------|------|---------|
| **Q** | 261.63 Hz | Do (C) | 4 |
| **S** | 293.66 Hz | Ré (D) | 4 |
| **D** | 329.63 Hz | Mi (E) | 4 |
| **F** | 349.23 Hz | Fa (F) | 4 |
| **G** | 392.00 Hz | Sol (G) | 4 |
| **H** | 440.00 Hz | La (A) | 4 |
| **J** | 493.88 Hz | Si (B) | 4 |
| **K** | 523.25 Hz | Do (C) | 5 |
| **L** | 587.33 Hz | Ré (D) | 5 |

#### Touches Noires (Notes altérées)

| Touche | Fréquence | Note | Octave |
|--------|-----------|------|---------|
| **A** | 277.18 Hz | Do# (C#) | 4 |
| **E** | 311.13 Hz | Ré# (D#) | 4 |
| **T** | 369.99 Hz | Fa# (F#) | 4 |
| **Y** | 415.30 Hz | Sol# (G#) | 4 |
| **U** | 466.16 Hz | La# (A#) | 4 |
| **O** | 554.37 Hz | Do# (C#) | 5 |
| **P** | 622.25 Hz | Ré# (D#) | 5 |

---

## ✨ Fonctionnalités

✅ **Polyphonie** - Jouez plusieurs notes simultanément
✅ **Sans glitchs** - Continuité de phase entre les blocs audio
✅ **Oscilloscope temps réel** - Visualisez les ondes au fur et à mesure
✅ **Multiples formes d'ondes** - Sinus, Carré, Triangle, Dents de scie
✅ **Fade-out naturel** - Résonance après relâchement des touches
✅ **Clavier intuitif** - Disposition en deux rangées comme un vrai piano

---

## 🔧 Détails Techniques

### Paramètres Audio

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Fréquence d'échantillonnage (fs)** | 44100 Hz | Qualité CD|
| **Durée bloc audio** | 50 ms | Intervalle de génération |
| **Taille affichage** | 30 ms | Données visibles en live |
| **Intervalle timer** | 25 ms | Mise à jour graphique |
| **Délai fade-out** | 10 ms | Période d'attente |

### Formules Mathématiques

Pour chaque fréquence dans la polyphonie :

$$\text{signal}(t) = \text{wave_type}(2\pi f t + \phi(t))$$

La phase est accumulée entre les blocs pour éviter les discontinuités :

$$\phi_{n+1} = (\phi_n + 2\pi f \Delta t) \bmod 2\pi$$

où $\Delta t = 50 \text{ ms}$ (durée du bloc).

---

## 🐛 Dépannage

### L'application ne génère pas de son
- Vérifiez que votre périphérique audio est connecté et défini par défaut dans les paramètres système
- Testez avec `python -c "import sounddevice; print(sounddevice.default_device())"`

### Sons saccadés ou glitchés
- Vérifiez que votre CPU n'est pas surchargé
- Réduisez le nombre d'ondes affichées dans l'oscilloscope

### Interface lente
- Fermez les autres applications gourmandes en ressources
- La génération d'audio prend priorité sur l'affichage

---

## 📝 Notes D'implémentation

1. **Continuité de phase** : Chaque bloc de 50ms accumule sa phase pour le bloc suivant, garantissant une transition sans clic audio.

2. **Polyphonie** : Les fréquences sont stockées dans un set, permettant des notes multiples sans doublons.

3. **Timers Qt** : 
   - Timer principal (25ms) : génère les blocs audio
   - Release timer (10ms) : gère le fade-out après relâchement

4. **Buffer d'affichage** : Limité à 30ms de données pour une visualisation réactive sans croissance mémoire infinie.

5. **Normalisation** : Le signal combiné est normalisé pour respecter les limites [-1, +1] et éviter l'écrêtage.

---

## 📄 Licence

À définir selon vos besoins

---

## 👨‍💻 Développement

Le code est organisé selon le pattern Model-View-Controller : - **Model** : `SignalGenerator` et `AudioEngine`
- **View** : `SynthInterface`
- **Controller** : Classe `App` dans `main.py`

Pour contribuer au projet, modifiez les modules spécifiques et maintenez la séparation des responsabilités.
À définir selon vos besoins
