import os

from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """LLM config shared by every agent and by the group chat manager."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to the .env file "
            "in the project root."
        )

    return {
        "config_list": [
            {
                "model": "gpt-4o-mini",
                "api_key": api_key,
            }
        ],
        "temperature": 0.3,
        "timeout": 120,
        "cache_seed": None,
    }
