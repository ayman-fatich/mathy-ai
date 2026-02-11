import anthropic
import re
from app.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_system_prompt(provider: str) -> str:
    base = """
You are a Manim Expert. Create educational videos.
RULES:
1. LAYOUT: Use VGroups and .scale_to_fit_width(12).
2. ASSETS: NO external images. Use built-in shapes (Star, Circle, Text).
3. LANGUAGE: Detect user language and use it.
"""
    if provider == "elevenlabs":
        return base + """
4. AUDIO: Use ElevenLabsService.
   - Import: from manim_voiceover.services.elevenlabs import ElevenLabsService
   - Init: self.set_speech_service(ElevenLabsService(voice_name="Adam", model="eleven_multilingual_v2", transcription_model=None))
5. SYNC: with self.voiceover(text="...") as tracker: self.play(..., run_time=tracker.duration)
"""
    elif provider == "google":
        return base + """
4. AUDIO: Use GTTSService.
   - Import: from manim_voiceover.services.gtts import GTTSService
   - Init: self.set_speech_service(GTTSService())
5. SYNC: with self.voiceover(text="...") as tracker: self.play(..., run_time=tracker.duration)
"""
    else:
        return base + "4. AUDIO: None. Inherit from Scene. Use self.wait() for timing."

def generate_code(prompt: str, provider: str, context: str) -> str:
    system_prompt = get_system_prompt(provider)
    user_msg = f"CURRENT CODE:\n{context}\n\nREQ: {prompt}" if context else f"Create a Manim video about: {prompt}"
    
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-5-20250929", max_tokens=4000, system=system_prompt,
            messages=[{"role": "user", "content": user_msg}]
        )
        raw = msg.content[0].text
        match = re.search(r"```(?:python)?\s*(.*?)\s*```", raw, re.DOTALL)
        return match.group(1) if match else raw
    except Exception as e:
        raise Exception(f"AI Error: {str(e)}")
