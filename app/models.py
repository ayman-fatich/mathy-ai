from pydantic import BaseModel
from typing import Literal

class VideoRequest(BaseModel):
    prompt: str
    provider: Literal["elevenlabs", "google", "none"] = "elevenlabs"
