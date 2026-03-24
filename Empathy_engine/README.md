# 🎙 The Empathy Engine

An emotionally aware Text-to-Speech (TTS) service that detects the underlying emotion in input text and dynamically modulates the synthetic voice to perfectly match the mood — speaking rapidly when ecstatic, calmly when neutral, and slowly with deeper pitch when sad.

---

## Features

- **7 Emotion Categories:** Ecstatic, Excited, Happy, Neutral, Concerned, Sad, Furious
- **Dynamic Vocal Modulation:** Intelligently adjusts 3 key Pyttsx3 parameters: Rate (wpm), Volume, and Pitch.
- **Intensity Scaling:** Stronger emotions produce more extreme vocal changes using VADER compound score multipliers.
- **Web Interface:** Paste text, view detailed voice parameter analytics, and play audio directly in your browser.
- **CLI Mode:** Run an expansive 7-emotion demo suite directly from the terminal.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone [<your-repo-url>](https://github.com/venu-gopal12/Assign.git)
cd empathy_engine
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# On Windows: 
venv\Scripts\activate
# On Mac/Linux: 
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note for Linux users:** pyttsx3 requires `espeak`:
> ```bash
> sudo apt-get install espeak
> ```

---

## Running the App

### Option A — Web Interface (Recommended)
```bash
python web_app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser. Simply type your text, click "Synthesize Speech", and let the Empathy Engine analyze your emotion.

### Option B — CLI Demo
```bash
python app.py
```
This automatically processes a test suite of 7 distinctive sentences encompassing every registered emotion and saves them locally as `.wav` files (e.g. `ecstatic.wav`, `sad.wav`, `furious.wav`).

---

## Design Choices

### Emotion Detection
We utilize **VADER (Valence Aware Dictionary and sEntiment Reasoner)** from the `vaderSentiment` library. VADER is purpose-built for short, expressive social text and returns a compound score from -1.0 (most negative) to +1.0 (most positive). 

We meticulously map this scale into 7 granular psychological buckets:

| Compound Score | Assigned Emotion |
|----------------|------------------|
| ≥ 0.8          | Ecstatic         |
| ≥ 0.5          | Excited          |
| ≥ 0.1          | Happy            |
| > -0.1         | Neutral          |
| ≥ -0.3         | Concerned        |
| ≥ -0.7         | Sad              |
| < -0.7         | Furious          |

### Emotion → Voice Mapping
| Emotion   | Base Rate (wpm) | Base Volume | Base Pitch | Notes                    |
|-----------|-----------------|-------------|------------|--------------------------|
| Ecstatic  | 240             | 1.0         | 90         | Bright, extremely fast   |
| Excited   | 210             | 1.0         | 80         | Fast, loud               |
| Happy     | 190             | 0.9         | 65         | Upbeat                   |
| Neutral   | 170             | 0.8         | 50         | Baseline standard        |
| Concerned | 150             | 0.75        | 40         | Cautious, quieter        |
| Sad       | 120             | 0.6         | 25         | Slowest, most subdued    |
| Furious   | 220             | 1.0         | 15         | Fast, tense, low pitch   |

### Intensity Scaling
The absolute value of the VADER compound score (0.0–1.0) serves as an intensity multiplier. A slightly unhappy sentence gets a small rate/pitch drop; a profoundly devastating "Sad" sentence receives a dramatic deceleration.
