import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import QuestDesignBrief, Quest, RegenerateSectionRequest
from .quest_generator import generate_quest, regenerate_section

app = FastAPI(
    title="Quest Narrative Designer API",
    description="Generate structured quests from design briefs using an LLM.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
INDEX_HTML = STATIC_DIR / "index.html"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(str(INDEX_HTML))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/quests/generate", response_model=Quest)
async def create_quest(brief: QuestDesignBrief):
    try:
        quest = await generate_quest(brief)
        return quest
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quests/regenerate", response_model=Quest)
async def regenerate_quest_section(payload: RegenerateSectionRequest):
    try:
        quest = await regenerate_section(payload)
        return quest
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
