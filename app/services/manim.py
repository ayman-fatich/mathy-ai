import os
import subprocess
import time
from app.config import BASE_DIR, ELEVENLABS_API_KEY

def render_scene(code: str, provider: str) -> str:
    # 1. Inject Keys/Fixes for ElevenLabs
    if provider == "elevenlabs":
        code = code.replace("eleven_monolingual_v1", "eleven_multilingual_v2")
        # Inject Key
        if "ElevenLabsService(" in code:
            code = code.replace("ElevenLabsService(", f'ElevenLabsService(api_key="{ELEVENLABS_API_KEY}", transcription_model=None, ')
        # Global Backup
        if "from elevenlabs import set_api_key" not in code:
            code = "from elevenlabs import set_api_key\n" + code
        if "def construct(self):" in code:
            code = code.replace("def construct(self):", f"def construct(self):\n        set_api_key('{ELEVENLABS_API_KEY}')\n")
        # Cleanup duplicates
        code = code.replace("transcription_model=None, transcription_model=None", "transcription_model=None")

    # 2. Write File
    filename = "gen_scene.py"
    filepath = BASE_DIR / filename
    with open(filepath, "w") as f:
        # Ensure imports exist
        if provider != "none" and "from manim import *" not in code:
             f.write("from manim import *\nfrom manim_voiceover import VoiceoverScene\n")
             if provider == "elevenlabs": f.write("from manim_voiceover.services.elevenlabs import ElevenLabsService\n")
             elif provider == "google": f.write("from manim_voiceover.services.gtts import GTTSService\n")
        f.write(code)

    # 3. Render
    unique_id = f"render_{int(time.time())}"
    print(f"🎬 Rendering: {unique_id}")
    
    # Run Docker (-ql = 480p low quality for speed)
    cmd = f"manim -ql {filename} -o {unique_id}"
    
    res = subprocess.run([
        "docker", "run", "--rm", 
        "-v", f"{str(BASE_DIR)}:/manim", 
        "-u", "root", 
        "mathy-runner", 
        "/bin/sh", "-c", cmd
    ], capture_output=True, text=True)

    if res.returncode != 0:
        raise Exception(f"Render Failed: {res.stderr}")
    
    return f"{unique_id}.mp4"
