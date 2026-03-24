"""
Empathy Engine - Web Interface (Flask)
Run with: python web_app.py
Then open http://localhost:5000
"""

from flask import Flask, request, render_template_string, send_file, jsonify
import os
from app import run  # imports our pipeline from app.py

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🎙 The Empathy Engine</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 700px; margin: 60px auto; background: #1a1a1a; color: #f4f4f4; }
        h1   { color: #ffffff; text-align: center; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #aaa; margin-bottom: 30px; }
        
        .container { background: #2c2c2c; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        
        textarea { width: 100%; height: 120px; padding: 12px; font-size: 16px; border-radius: 8px; border: 1px solid #444; background: #3a3a3a; color: white; box-sizing: border-box; resize: vertical; }
        textarea:focus { outline: none; border-color: #4a90e2; }
        
        button { margin-top: 15px; width: 100%; padding: 14px 28px; background: #4a90e2; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #357abd; }
        button:disabled { background: #555; cursor: not-allowed; }

        .loading { display: none; text-align: center; margin-top: 30px; color: #4a90e2; font-weight: bold; font-size: 1.1em; }
        .loading.active { display: block; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

        .result { display: none; margin-top: 30px; background: #222; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; animation: fadeIn 0.5s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .emotion-badge { display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: bold; color: white; margin-bottom: 20px; text-transform: uppercase; font-size: 16px; letter-spacing: 1px; }
        .ecstatic   { background: #f1c40f; color: #333; }
        .excited    { background: #e67e22; }
        .happy      { background: #2ecc71; }
        .neutral    { background: #7f8c8d; }
        .concerned  { background: #e74c3c; }
        .sad        { background: #3498db; }
        .furious    { background: #c0392b; }

        .stats { color: #bbb; font-size: 16px; margin-bottom: 25px; background: #333; padding: 15px; border-radius: 8px; display: inline-block;}
        
        audio { width: 100%; outline: none; }
    </style>
</head>
<body>
    <h1>🎙 The Empathy Engine</h1>
    <p class="subtitle">Dynamically modulating vocal characteristics based on detected emotion.</p>
    
    <div class="container">
        <form id="gen-form">
            <textarea id="text-input" placeholder="Type a sentence here... e.g., 'I just got the promotion I've been working towards for years!'"></textarea>
            <button type="submit" id="submit-btn">Synthesize Speech</button>
        </form>
    </div>

    <div class="loading" id="loader">Analyzing emotion and generating audio...</div>

    <div class="result" id="result-box">
        <span class="emotion-badge" id="emotion-badge">NEUTRAL</span>
        <br>
        <div class="stats" id="stats-box">
            <strong>Rate:</strong> <span id="val-rate"></span> wpm &nbsp;|&nbsp; 
            <strong>Volume:</strong> <span id="val-vol"></span> &nbsp;|&nbsp; 
            <strong>Pitch:</strong> <span id="val-pitch"></span>
        </div>
        
        <audio id="audio-player" controls></audio>
    </div>

    <script>
        const form = document.getElementById('gen-form');
        const btn = document.getElementById('submit-btn');
        const loader = document.getElementById('loader');
        const resultBox = document.getElementById('result-box');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = document.getElementById('text-input').value.trim();
            if (!text) return;

            // UI Loading state
            btn.disabled = true;
            resultBox.style.display = 'none';
            loader.classList.add('active');

            try {
                const fd = new FormData();
                fd.append('text', text);

                const res = await fetch('/api/generate', { method: 'POST', body: fd });
                const data = await res.json();

                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    // Update DOM
                    document.getElementById('emotion-badge').className = 'emotion-badge ' + data.emotion;
                    document.getElementById('emotion-badge').innerText = data.emotion;
                    
                    document.getElementById('val-rate').innerText = data.params.rate;
                    document.getElementById('val-vol').innerText = data.params.volume.toFixed(2);
                    document.getElementById('val-pitch').innerText = data.params.pitch;
                    
                    // Add a tiny random parameter to the audio URL to force browser cache bypass
                    const audio = document.getElementById('audio-player');
                    audio.src = `/audio?t=${new Date().getTime()}`;
                    audio.play();

                    resultBox.style.display = 'block';
                }
            } catch (err) {
                alert('Generation failed: ' + err);
            } finally {
                btn.disabled = false;
                loader.classList.remove('active');
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/generate", methods=["POST"])
def generate():
    text = request.form.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Run Empathy TTS Generation (this saves audio to outputs.wav)
        emotion, params = run(text, output_path="output.wav")
        
        return jsonify({
            "emotion": emotion,
            "params": params
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/audio")
def audio():
    return send_file("output.wav", mimetype="audio/wav")

if __name__ == "__main__":
    app.run(debug=True)
