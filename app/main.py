from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.models import VideoRequest
from app.services.llm import generate_code
from app.services.manim import render_scene
from app.config import MEDIA_DIR, BASE_DIR

app = FastAPI()

# Mount Static Files
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")

# In-memory session state
session = {"code": ""}

@app.get("/")
async def serve_ui():
    return FileResponse(BASE_DIR / "frontend/index.html")

@app.post("/generate")
async def generate(req: VideoRequest):
    print(f"🧠 Processing: {req.prompt} ({req.provider})")
    try:
        # 1. AI Generation
        code = generate_code(req.prompt, req.provider, session["code"])
        session["code"] = code
        
        # 2. Rendering
        filename = render_scene(code, req.provider)
        
        return {
            "status": "success", 
            "video_path": f"/media/videos/gen_scene/480p15/{filename}"
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "log": str(e)}
