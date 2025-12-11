import os
import json
from typing import Any, Dict

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


class LLMClient:
    """
    Thin wrapper around the OpenAI ChatCompletion API.
    Replace or extend this class if you want to use a different provider.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        env_model = os.getenv("OPENAI_MODEL")
        self.model = env_model or model

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        self.client = OpenAI(api_key=api_key)

    def complete_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Call the chat completion API and expect a JSON object in the response.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
        )
        content = response.choices[0].message.content
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[len("json"):]
            content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {e}\nRaw: {content}")
