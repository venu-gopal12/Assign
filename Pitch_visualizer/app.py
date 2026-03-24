"""
Pitch Visualizer - From Words to Storyboard
Uses Groq (free) for prompt engineering + Hugging Face for images.
"""

import os
import re
import requests
from openai import OpenAI

# ── Configuration ─────────────────────────────────────────────────────────────

GROQ_API_KEY   = os.getenv("GROQ_API_KEY",   "")
HF_API_KEY     = os.getenv("HF_API_KEY",     "")

groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

VISUAL_STYLE = "cinematic digital art, professional lighting, highly detailed"


# ── Step 1: Narrative Segmentation ───────────────────────────────────────────

def segment_text(text: str) -> list[str]:
    """Splits text into full sentences only (.!?). Never splits on commas."""
    text = text.strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if len(sentences) < 3:
        words = text.split()
        chunks, current = [], []
        for word in words:
            current.append(word)
            if len(" ".join(current)) >= 80:
                chunks.append(" ".join(current))
                current = []
        if current:
            chunks.append(" ".join(current))
        sentences = [c for c in chunks if len(c) > 10]

    print(f"\n  Segmented into {len(sentences)} scenes:")
    for i, s in enumerate(sentences):
        print(f"    {i+1}. {s}")

    return sentences[:6]


# ── Step 2: Prompt Engineering (Groq) ────────────────────────────────────────

def engineer_prompt(sentence: str, scene_number: int, total_scenes: int) -> str:
    """Uses Groq LLaMA to generate a rich visual image prompt."""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a visual art director. Transform the sentence into an image generation prompt. "
                    "Max 35 words. Focus on setting, lighting, mood, colors. "
                    "No text or words in image. Return ONLY the prompt."
                )
            },
            {
                "role": "user",
                "content": f"Scene {scene_number}/{total_scenes}: \"{sentence}\""
            }
        ],
        max_tokens=80,
        temperature=0.7
    )
    engineered = response.choices[0].message.content.strip()
    return f"{engineered}, {VISUAL_STYLE}"


# ── Step 3: Image Generation (Hugging Face) ──────────────────────────────────

def generate_and_save_image(prompt: str, scene_index: int, output_dir: str) -> str:
    """
    Generates an image using Hugging Face Inference API and saves it locally.
    """
    print(f"  🎨 Generating image for scene {scene_index + 1} via Hugging Face...")
    print(f"     Prompt: {prompt[:70]}...")

    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

    payload = {"inputs": prompt}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            filename = f"scene_{scene_index + 1}.png"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"  ✅ Image saved to: {filepath}")
            return filename
        else:
            print(f"  ❌ Error generating image: {response.status_code} - {response.text}")
    except Exception as e:
         print(f"  ❌ Exception during generation: {e}")

    # Fallback placeholder if generation fails
    fallback_url = "https://via.placeholder.com/1024x512.png?text=Generation+Failed"
    return fallback_url


# ── Step 4: Storyboard HTML ───────────────────────────────────────────────────

def build_storyboard_html(panels: list[dict], output_path: str):
    panel_html = ""
    for i, panel in enumerate(panels):
        delay = i * 0.12
        panel_html += f"""
        <div class="scene-card" style="animation-delay: {delay}s;">
            <div class="badge">Scene {i + 1}</div>
            <div class="img-wrap">
                <img src="{panel['image_path']}" alt="Scene {i + 1}" loading="lazy">
            </div>
            <div class="caption">{panel['sentence']}</div>
            <div class="prompt-area">
                <details>
                    <summary>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                        View engineered prompt
                    </summary>
                    <p class="prompt-text">{panel['prompt']}</p>
                </details>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📽 Pitch Visualizer Storyboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --background: #09090b;
            --foreground: #fafafa;
            --primary: #d4a853;
            --primary-foreground: #1a1a2e;
            --card: #18181b;
            --border: #27272a;
            --muted: #27272a;
            --muted-foreground: #a1a1aa;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: 'Inter', sans-serif; 
            background: var(--background); 
            color: var(--foreground); 
            min-height: 100vh;
        }}
        .font-display {{ font-family: 'Playfair Display', serif; }}
        
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        header {{ text-align: center; padding: 64px 24px 32px; animation: slideUp 0.6s ease-out forwards; }}
        h1 {{ font-size: 2.5rem; margin-bottom: 8px; }}
        .subtitle {{ color: var(--muted-foreground); font-size: 1rem; }}
        
        .grid {{
            max-width: 1200px; margin: 0 auto; padding: 0 24px 64px;
            display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px;
        }}
        
        .scene-card {{
            background: var(--card); border: 1px solid var(--border); border-radius: 12px;
            overflow: hidden; opacity: 0; animation: slideUp 0.6s ease-out forwards;
            transition: box-shadow 0.3s ease, border-color 0.3s ease;
            display: flex; flex-direction: column;
        }}
        .scene-card:hover {{ border-color: rgba(212,168,83,0.5); box-shadow: 0 0 30px -10px rgba(212,168,83,0.15); }}
        
        .badge {{
            background: var(--primary); color: var(--primary-foreground); text-align: center;
            padding: 6px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em;
        }}
        
        .img-wrap {{ width: 100%; aspect-ratio: 16/9; background: var(--muted); overflow: hidden; }}
        .img-wrap img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s ease; display: block; }}
        .scene-card:hover .img-wrap img {{ transform: scale(1.05); }}
        
        .caption {{ padding: 16px; font-size: 0.95rem; line-height: 1.6; border-top: 1px solid var(--border); flex-grow: 1; }}
        
        .prompt-area {{ padding: 0 16px 16px; }}
        details {{ transition: all 0.3s; }}
        summary {{ cursor: pointer; color: var(--muted-foreground); font-size: 0.8rem; display: flex; align-items: center; gap: 6px; font-weight: 500; }}
        summary:hover {{ color: var(--primary); }}
        summary::-webkit-details-marker {{ display: none; }}
        .prompt-text {{ margin-top: 12px; font-size: 0.8rem; color: #888; font-style: italic; line-height: 1.5; }}
    </style>
</head>
<body>
    <header>
        <h1 class="font-display">Your Storyboard</h1>
        <p class="subtitle">{len(panels)} scenes generated from your narrative</p>
    </header>
    
    <div class="grid">{panel_html}</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  ✅ Storyboard saved to: {output_path}")


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run(text: str, output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)
    print("\n═══════════════════════════════════")
    print("  📽  PITCH VISUALIZER")
    print("═══════════════════════════════════")

    sentences = segment_text(text)
    panels = []

    for i, sentence in enumerate(sentences):
        print(f"\n── Scene {i+1} ──────────────────────────")
        print(f"  🧠 Engineering visual prompt...")
        prompt = engineer_prompt(sentence, i + 1, len(sentences))
        print(f"  Prompt: {prompt[:80]}...")

        image_path = generate_and_save_image(prompt, i, output_dir)
        panels.append({"sentence": sentence, "prompt": prompt, "image_path": image_path})

    storyboard_path = os.path.join(output_dir, "storyboard.html")
    build_storyboard_html(panels, storyboard_path)
    print(f"\n  🎉 Done! Open {storyboard_path} in your browser.\n")
    return storyboard_path


if __name__ == "__main__":
    sample_text = (
        "Our client was drowning in manual data entry, spending 40 hours a week on repetitive tasks. "
        "After integrating our AI platform, their team was freed to focus on strategic work. "
        "Within three months, productivity soared by 60% and employee satisfaction reached an all-time high. "
        "Today, they are scaling their business faster than ever before."
    )
    run(sample_text)