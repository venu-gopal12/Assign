import os
import threading
from flask import Flask, request, render_template_string, jsonify, send_from_directory
import app as pipeline 

# 1. Define the absolute path to your output folder
OUTPUT_PATH = os.path.abspath("output")
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

# 2. Tell Flask that 'output' is where static files (images) live
app = Flask(__name__, static_folder=OUTPUT_PATH)

status = {"state": "idle", "message": ""}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📽 Pitch Visualizer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            --background: #09090b;
            --foreground: #fafafa;
            --primary: #d4a853;
            --primary-foreground: #1a1a2e;
            --card: #18181b;
            --border: #27272a;
            --muted: #27272a;
            --muted-foreground: #a1a1aa;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Inter', sans-serif; 
            background: var(--background); 
            color: var(--foreground); 
            min-height: 100vh;
            overflow-x: hidden;
        }
        .font-display { font-family: 'Playfair Display', serif; }
        
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        header {
            position: relative;
            text-align: center;
            padding: 80px 24px;
            background: radial-gradient(circle at top, rgba(212,168,83,0.1), transparent 70%);
        }
        .hero-pattern {
            position: absolute; inset: 0; opacity: 0.03; pointer-events: none;
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4a853' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        .header-content { position: relative; z-index: 10; opacity: 0; animation: slideUp 0.8s ease-out forwards; }
        h1 { font-size: 3.5rem; letter-spacing: -0.02em; margin-bottom: 16px; }
        h1 span { color: var(--primary); }
        .subtitle { color: var(--muted-foreground); font-size: 1.125rem; max-width: 450px; margin: 0 auto; line-height: 1.5; }
        
        main {
            max-width: 768px;
            margin: -24px auto 64px;
            padding: 0 24px;
            position: relative;
            z-index: 20;
            opacity: 0;
            animation: slideUp 0.6s ease-out 0.3s forwards;
        }
        .card {
            background: var(--card); border: 1px solid var(--border); border-radius: 12px;
            padding: 24px; box-shadow: 0 0 40px -10px rgba(212, 168, 83, 0.15);
            transition: box-shadow 0.3s ease;
        }
        .card:hover { box-shadow: 0 0 40px -5px rgba(212, 168, 83, 0.25); }
        
        label {
            display: block; font-size: 0.875rem; color: var(--muted-foreground);
            text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; font-weight: 600;
        }
        textarea {
            width: 100%; height: 140px; background: var(--background);
            border: 1px solid var(--border); border-radius: 8px;
            padding: 16px; color: var(--foreground); font-family: 'Inter', sans-serif;
            font-size: 0.95rem; line-height: 1.6; resize: vertical; transition: all 0.2s;
        }
        textarea:focus { outline: none; border-color: rgba(212, 168, 83, 0.5); box-shadow: 0 0 0 2px rgba(212, 168, 83, 0.2); }
        
        .style-select-wrap { margin-top: 20px; }
        select {
            width: 100%; background: var(--background); border: 1px solid var(--border);
            border-radius: 8px; padding: 12px; color: var(--foreground); font-family: 'Inter', sans-serif;
            transition: all 0.2s; appearance: none; outline: none;
        }
        select:focus { border-color: rgba(212, 168, 83, 0.5); }
        
        button.btn-primary {
            display: flex; align-items: center; justify-content: center; gap: 8px;
            width: 100%; margin-top: 24px; padding: 14px;
            background: var(--primary); color: var(--primary-foreground);
            border: none; border-radius: 8px; font-family: 'Playfair Display', serif;
            font-size: 1.125rem; font-weight: 700; cursor: pointer; transition: all 0.2s;
        }
        button.btn-primary:hover { filter: brightness(1.1); transform: translateY(-1px); }
        button.btn-primary:active { transform: translateY(1px); }
        button.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
        
        #status-area {
            display: none; text-align: center; margin-top: 40px; opacity: 0;
            animation: fadeIn 0.4s ease-out forwards;
        }
        .status-pill {
            display: inline-flex; align-items: center; gap: 12px;
            background: var(--card); border: 1px solid var(--border);
            padding: 12px 24px; border-radius: 99px; color: var(--muted-foreground); font-size: 0.9rem;
        }
        .spinner {
            width: 18px; height: 18px; border: 2px solid transparent; border-top-color: var(--primary);
            border-right-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite;
        }
        .spinner-btn { border-top-color: var(--primary-foreground); border-right-color: var(--primary-foreground); }
        
        #open-btn {
            display: none; align-items: center; justify-content: center; gap: 8px;
            padding: 12px 28px; background: transparent; color: var(--primary);
            border: 1px solid var(--primary); border-radius: 8px; margin: 24px auto 0;
            font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; transition: all 0.2s;
        }
        #open-btn:hover { background: rgba(212, 168, 83, 0.1); }
        
        footer { text-align: center; color: var(--muted-foreground); font-size: 0.8rem; padding: 20px 0 40px; }
    </style>
</head>
<body>
    <header>
        <div class="hero-pattern"></div>
        <div class="header-content">
            <h1 class="font-display">Pitch <span>Visualizer</span></h1>
            <p class="subtitle">Transform your narrative into a cinematic storyboard</p>
        </div>
    </header>

    <main>
        <div class="card">
            <label>Your Pitch Narrative</label>
            <textarea id="textInput" placeholder="e.g. Our client was drowning in manual work. After our solution, their productivity soared. Today they are scaling faster than ever."></textarea>
            
            <div class="style-select-wrap">
                <label>Visual Style</label>
                <select id="styleSelect">
                    <option value="cinematic digital art, professional lighting">Cinematic</option>
                    <option value="watercolor illustration, soft pastel tones">Watercolor</option>
                    <option value="photorealistic, 8k resolution, highly detailed">Photorealistic</option>
                    <option value="flat design vector art, bold colors">Flat Design</option>
                    <option value="dark moody oil painting, dramatic contrast">Dramatic</option>
                </select>
            </div>

            <button id="generateBtn" class="btn-primary" onclick="generate()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                Generate Storyboard
            </button>
        </div>

        <div id="status-area">
            <div class="status-pill">
                <div class="spinner" id="spinner"></div>
                <span id="statusMessage">Engineering prompts & generating scenes...</span>
            </div>
            <button id="open-btn" onclick="window.open('/storyboard', '_blank')">🎬 Open Storyboard</button>
        </div>
    </main>

    <footer>Powered by Groq + Hugging Face · Pitch Visualizer</footer>

    <script>
        async function generate() {
            const text = document.getElementById('textInput').value.trim();
            const style = document.getElementById('styleSelect').value;
            const btn = document.getElementById('generateBtn');
            const statusArea = document.getElementById('status-area');
            const statusMsg = document.getElementById('statusMessage');
            const spinner = document.getElementById('spinner');
            const openBtn = document.getElementById('open-btn');

            if (!text) { alert('Please enter some text first.'); return; }

            btn.disabled = true;
            btn.innerHTML = `<div class="spinner spinner-btn"></div> Crafting your storyboard...`;
            
            statusArea.style.display = 'block';
            statusMsg.innerText = 'Initializing generation pipeline...';
            spinner.style.display = 'block';
            openBtn.style.display = 'none';

            try {
                const resp = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, style })
                });

                const poll = setInterval(async () => {
                    const s = await fetch('/status').then(r => r.json());
                    statusMsg.innerText = s.message;
                    if (s.state === 'done') {
                        clearInterval(poll);
                        spinner.style.display = 'none';
                        statusMsg.innerText = '✅ Storyboard ready!';
                        openBtn.style.display = 'inline-flex';
                        btn.disabled = false;
                        btn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg> Generate Again`;
                    } else if (s.state === 'error') {
                        clearInterval(poll);
                        spinner.style.display = 'none';
                        statusMsg.innerText = '❌ Error: ' + s.message;
                        btn.disabled = false;
                        btn.innerHTML = `Generate Storyboard`;
                    }
                }, 1500);
            } catch (err) {
                statusMsg.innerText = '❌ Request failed.';
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    text = data.get("text", "")
    style = data.get("style", "cinematic digital art, professional lighting")
    pipeline.VISUAL_STYLE = style

    def task():
        status["state"] = "running"
        try:
            status["message"] = "Generating scenes..."
            # Always use the absolute path for the pipeline
            pipeline.run(text, output_dir=OUTPUT_PATH)
            status["state"] = "done"
            status["message"] = "Storyboard complete!"
        except Exception as e:
            status["state"] = "error"
            status["message"] = str(e)

    threading.Thread(target=task).start()
    return jsonify({"ok": True})

@app.route("/status")
def get_status():
    return jsonify(status)

@app.route("/storyboard")
def storyboard():
    return send_from_directory(OUTPUT_PATH, "storyboard.html")

# 3. This is the magic route that fixes the broken images
@app.route('/<path:filename>')
def serve_output_files(filename):
    return send_from_directory(OUTPUT_PATH, filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
