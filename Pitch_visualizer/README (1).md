# 📽 Pitch Visualizer

An AI-powered storyboard generator that transforms narrative text into a multi-panel visual storyboard. Paste a customer success story or sales pitch and instantly receive a stunning, image-rich HTML storyboard wrapped in a beautiful, premium cinematic web interface.

---

## Features

- **Automatic Scene Segmentation** — splits your narrative into logical visual scenes (sentences).
- **Blazing-Fast Prompt Engineering** — uses **Groq (LLaMA 3.3 70B)** to dynamically transform plain sentences into rich, vivid visual prompts.
- **High-Quality Image Generation** — utilizes the **Hugging Face Inference API** (Stable Diffusion XL) to generate stunning artwork per scene.
- **Consistent Visual Style** — select from Cinematic, Watercolor, Photorealistic, Flat Design, or Dramatic; applied cleanly to every panel.
- **Premium Web Interface** — designed with custom vanilla CSS featuring a gorgeous dark mode, glowing golden accents, and smooth CSS animations (slide-ups, fade-ins).
- **Local Caching** — images are saved locally so your HTML storyboard works perfectly offline and loads instantly.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd pitch_visualizer
```

### 2. Create a virtual environment
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

### 4. Set your API Keys
You will need a free API key from Groq and a free Access Token from Hugging Face.

```bash
# Windows (PowerShell)
$env:GROQ_API_KEY="gsk_your-key-here"
$env:HF_API_KEY="hf_your-token-here"

# Mac/Linux
export GROQ_API_KEY="gsk_your-key-here"
export HF_API_KEY="hf_your-token-here"
```

- **Groq Console:** [https://console.groq.com](https://console.groq.com)
- **Hugging Face Tokens:** [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

---

## Running the App

### Option A — Web Interface (Recommended)
```bash
python web_app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser. You will be greeted by the new premium interface. Paste your text, choose a style, and click **Generate Storyboard**. The UI provides live status polling and sleek loading animations.

### Option B — CLI
```bash
python app.py
```
Generates a storyboard from the built-in sample text directly in your terminal. Look in your `output` folder for the gorgeous `storyboard.html`.

---

## Design Choices

### Architecture Switch (Groq + Hugging Face)
We fully migrated away from OpenAI/DALL-E 3 to a **Groq + Hugging Face** pipeline to maximize speed and developer flexibility. 
- Prompt engineering is near-instantaneous via Groq's LPU inference engine.
- Image generation requests are routed through the Hugging Face Serverless API router for seamless integration.
- Built-in fallback mechanisms ensure your storyboard HTML never breaks, rendering placeholder panels gracefully if an endpoint times out.

### Visual Styling & UI
We completely ditched bootstrap/tailwind frameworks for a **100% vanilla custom CSS** layout. This avoids bloat while delivering an incredibly high-end aesthetic inspired by strict design systems:
- Exacting typography (`Playfair Display` headers and `Inter` body fonts)
- Intricate micro-interactions (`glow-gold` hover effects)
- Deep, immersive dark mode backgrounds (`#09090b`) matched with warm `primary` visual accents.
