import json
from textwrap import dedent
from typing import Any

from .models import QuestDesignBrief, Quest, RegenerateSectionRequest
from .llm_client import LLMClient


def _build_system_prompt() -> str:
    return dedent(
        """
        You are an experienced game narrative designer and systems designer.
        You design quests for modern online games with clear objectives,
        strong thematic coherence, and concise, production-ready text.

        Your task is to produce STRICT JSON that conforms exactly to the schema
        described by the user. Do not include any extra commentary, markdown,
        or explanations. Only output JSON.
        """
    ).strip()


def _build_quest_schema_description() -> str:
    return dedent(
        """
        The JSON object must have the following structure:

        {
          "title": string,
          "summary": string,
          "zone": string,
          "faction": string,
          "tone": string,
          "player_level_min": integer,
          "player_level_max": integer,
          "steps": [
            {
              "step_number": integer,
              "description": string,
              "objective": string,
              "npc_dialogue": [
                {
                  "speaker": must be exactly "NPC" or "PLAYER" (not a character name),
                  "text": string
                },
                ...
              ]
            },
            ...
          ],
          "rewards": [
            {
              "type": "xp" | "gold" | "item" | "cosmetic" | "other",
              "description": string,
              "amount": integer or null
            },
            ...
          ]
        }

        CRITICAL: In npc_dialogue entries:
        - "speaker" MUST be exactly the literal string "NPC" (when an NPC is speaking) or "PLAYER" (when the player is speaking).
        - Do NOT use character names like "Jora", "Guard", "Swamp Guardian" - these belong in the dialogue text, not as the speaker field.
        - Each dialogue line must indicate WHO is speaking using only "NPC" or "PLAYER".
        """
    ).strip()


def _build_user_prompt_from_brief(brief: QuestDesignBrief) -> str:
    brief_json = brief.model_dump()
    schema_desc = _build_quest_schema_description()
    return dedent(
        f"""
        Design a quest according to the following design brief and output
        a JSON object following the schema described below.

        DESIGN BRIEF (JSON):
        {json.dumps(brief_json, indent=2)}

        SCHEMA DESCRIPTION:
        {schema_desc}

        Additional requirements:
        - The quest should be thematically consistent with the zone and faction.
        - The tone field should be reflected in the writing style.
        - Use between {brief.number_of_steps} and {brief.number_of_steps} steps.
        - Keep text concise and production-ready.
        - Ensure all required fields are present and valid.
        - IMPORTANT: In dialogue exchanges, the "speaker" field must ONLY be "NPC" or "PLAYER" - never use character names or NPC identities as the speaker value. Character names and descriptions should appear in the dialogue text itself, not in the speaker field.
        """
    ).strip()


async def generate_quest(brief: QuestDesignBrief) -> Quest:
    client = LLMClient()
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt_from_brief(brief)
    result_dict: Any = client.complete_json(system_prompt, user_prompt)
    try:
        quest = Quest.model_validate(result_dict)
    except Exception as e:
        raise ValueError(f"LLM returned JSON that does not match Quest schema: {e}")
    return quest


def _build_regeneration_prompt(payload: RegenerateSectionRequest) -> str:
    schema_desc = _build_quest_schema_description()
    base = {
        "brief": payload.brief.model_dump(),
        "current_quest": payload.quest.model_dump(),
        "section": payload.section,
        "step_index": payload.step_index,
    }
    return dedent(
        f"""
        You are updating part of an existing quest specification.

        CURRENT DATA (JSON):
        {json.dumps(base, indent=2)}

        SCHEMA DESCRIPTION:
        {schema_desc}

        TASK:
        - Regenerate ONLY the requested section of the quest ("title", "summary", or "steps").
        - For "title" or "summary": keep the quest structure but update that field to be stronger and more engaging.
        - For "steps": regenerate the step at the given step_index (0-based index), keeping the rest of the quest intact.
        - Always return the FULL updated quest JSON object (not just the changed field).
        - Ensure the JSON still follows the schema exactly.
        """
    ).strip()


async def regenerate_section(payload: RegenerateSectionRequest) -> Quest:
    client = LLMClient()
    system_prompt = _build_system_prompt()
    user_prompt = _build_regeneration_prompt(payload)
    result_dict: Any = client.complete_json(system_prompt, user_prompt)
    try:
        quest = Quest.model_validate(result_dict)
    except Exception as e:
        raise ValueError(
            f"LLM returned JSON that does not match Quest schema on regeneration: {e}"
        )
    return quest
