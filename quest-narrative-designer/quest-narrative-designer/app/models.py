from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class QuestDesignBrief(BaseModel):
    zone: str = Field(..., description="Zone or environment where the quest takes place")
    faction: str = Field(..., description="Main faction or group involved in the quest")
    tone: str = Field(..., description="Tone of the quest, e.g., dark, hopeful, comedic")
    player_level_min: int = Field(..., ge=1, description="Minimum target player level")
    player_level_max: int = Field(..., ge=1, description="Maximum target player level")
    narrative_style: Optional[str] = Field(
        None, description="Optional style notes, e.g., epic, grounded, character-driven"
    )
    number_of_steps: int = Field(
        4, ge=3, le=8, description="Number of quest steps to generate"
    )
    target_playtime_minutes: Optional[int] = Field(
        None, description="Target playtime in minutes"
    )
    forbidden_elements: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of forbidden themes or elements (e.g., time travel, specific characters)"
        ),
    )


class NPCDialogueLine(BaseModel):
    speaker: Literal["NPC", "PLAYER"]
    text: str


class QuestStep(BaseModel):
    step_number: int
    description: str
    objective: str
    npc_dialogue: List[NPCDialogueLine]


class Reward(BaseModel):
    type: Literal["xp", "gold", "item", "cosmetic", "other"]
    description: str
    amount: Optional[int] = None


class Quest(BaseModel):
    title: str
    summary: str
    zone: str
    faction: str
    tone: str
    player_level_min: int
    player_level_max: int
    steps: List[QuestStep]
    rewards: List[Reward]


class RegenerateSectionRequest(BaseModel):
    brief: QuestDesignBrief
    quest: Quest
    section: Literal["title", "summary", "steps"]
    step_index: Optional[int] = Field(
        default=None,
        description="Index of the step to regenerate when section == 'steps'",
    )
