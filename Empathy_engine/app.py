"""
Empathy Engine - Emotionally Aware Text-to-Speech
Detects emotion in text and modulates voice accordingly.
"""

import pyttsx3
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── Emotion Detection ────────────────────────────────────────────────────────

def detect_emotion(text: str) -> dict:
    """
    Analyzes text and returns an emotion label + intensity score.
    Uses VADER which gives scores between -1 (most negative) and +1 (most positive).
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]  # overall score

    # Granular emotion mapping
    if compound >= 0.8:
        emotion = "ecstatic"
    elif compound >= 0.5:
        emotion = "excited"
    elif compound >= 0.1:
        emotion = "happy"
    elif compound > -0.1:
        emotion = "neutral"
    elif compound >= -0.3:
        emotion = "concerned"
    elif compound >= -0.7:
        emotion = "sad"
    else:
        emotion = "furious"

    return {"emotion": emotion, "intensity": abs(compound), "compound": compound}


# ── Voice Parameter Mapping ──────────────────────────────────────────────────

def get_voice_params(emotion: str, intensity: float) -> dict:
    """
    Maps emotion + intensity to voice parameters.
    
    rate  = words per minute  (default ~200)
    pitch = voice frequency   (0-100, but pyttsx3 uses 0-100 scale)
    volume= amplitude         (0.0 to 1.0)
    """

    # Base configurations per emotion
    base_configs = {
        "ecstatic":  {"rate": 240, "volume": 1.0,  "pitch": 90},
        "excited":   {"rate": 210, "volume": 1.0,  "pitch": 80},
        "happy":     {"rate": 190, "volume": 0.9,  "pitch": 65},
        "neutral":   {"rate": 170, "volume": 0.8,  "pitch": 50},
        "concerned": {"rate": 150, "volume": 0.75, "pitch": 40},
        "sad":       {"rate": 120, "volume": 0.6,  "pitch": 25},
        "furious":   {"rate": 220, "volume": 1.0,  "pitch": 15},
    }

    params = base_configs.get(emotion, base_configs["neutral"]).copy()

    # Intensity scaling: stronger emotion = more extreme parameters
    # intensity ranges from 0.0 to 1.0
    if emotion in ("ecstatic", "excited", "happy"):
        params["rate"]   += int(30 * intensity)   # faster for stronger positivity
        params["pitch"]  += int(20 * intensity)   # higher pitch
    elif emotion in ("sad", "concerned"):
        params["rate"]   -= int(25 * intensity)   # slower for sadness/concern
        params["pitch"]  -= int(15 * intensity)   # lower pitch
    elif emotion == "furious":
        params["rate"]   += int(40 * intensity)   # anger speeds up
        params["pitch"]  -= int(20 * intensity)   # tense, low pitch

    # Clamp values to safe ranges
    params["rate"]   = max(80, min(300, params["rate"]))
    params["pitch"]  = max(0,  min(100, params["pitch"]))
    params["volume"] = max(0.1, min(1.0, params["volume"]))

    return params


# ── TTS Engine ───────────────────────────────────────────────────────────────

def speak_and_save(text: str, params: dict, output_path: str = "output.wav"):
    """
    Uses pyttsx3 to synthesize speech with given params and save to a WAV file.
    """
    engine = pyttsx3.init()

    engine.setProperty("rate",   params["rate"])
    engine.setProperty("volume", params["volume"])

    # pyttsx3 pitch control varies by driver; this sets it where supported
    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)  # use default voice

    engine.save_to_file(text, output_path)
    engine.runAndWait()
    print(f"  Audio saved to: {output_path}")


# ── Main Pipeline ────────────────────────────────────────────────────────────

def run(text: str, output_path: str = "output.wav"):
    """Full pipeline: text → emotion → voice params → audio file."""
    print("\n═══════════════════════════════════")
    print("  🎙  EMPATHY ENGINE")
    print("═══════════════════════════════════")
    print(f"  Input : \"{text}\"")

    # Step 1: Detect emotion
    result   = detect_emotion(text)
    emotion  = result["emotion"]
    intensity= result["intensity"]
    print(f"  Emotion  : {emotion.upper()} (intensity: {intensity:.2f})")

    # Step 2: Get voice parameters
    params = get_voice_params(emotion, intensity)
    print(f"  Rate     : {params['rate']} wpm")
    print(f"  Volume   : {params['volume']}")
    print(f"  Pitch cfg: {params['pitch']}")

    # Step 3: Generate audio
    speak_and_save(text, params, output_path)
    print("═══════════════════════════════════\n")
    return emotion, params


# ── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Demo with different emotions covering every Empathy Engine category
    examples = [
        ("I am so incredibly thrilled and unbelievably overjoyed! It is an absolutely perfect miracle!", "ecstatic.wav"),
        ("This is so awesome! I got the promotion and I can't wait to start!", "excited.wav"),
        ("This coffee is pretty good, I really like it.", "happy.wav"),
        ("The meeting is scheduled for 3pm tomorrow in the conference room.", "neutral.wav"),
        ("I'm a little worried about these falling metrics, we should be careful.", "concerned.wav"),
        ("I'm just so tired. It feels like no matter how hard I try, nothing ever changes.", "sad.wav"),
        ("I am absolutely outraged and angry! This is the worst experience of my life!", "furious.wav"),
    ]

    for text, filename in examples:
        run(text, output_path=filename)

