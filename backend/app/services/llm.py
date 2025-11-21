"""Thin wrapper to call the configured chat LLM."""
import logging
import requests
from requests import RequestException

from app.core.config import settings

logger = logging.getLogger(__name__)

async def call_llm(messages: list[dict]) -> str:
    """Send a chat-style request to the LLM and return the content string."""
    payload = {
        "model": "deepseek-r1:1.5b",
        "messages": messages,
        "stream": False
    }
    url = f"{settings.ollama_url}/api/chat"

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except RequestException as exc:
        logger.error("LLM request failed: %s", exc)
        raise RuntimeError(f"LLM request failed: {exc}") from exc
    except KeyError:
        logger.error("LLM response missing expected content: %s", response.text if 'response' in locals() else "no response")
        raise RuntimeError("LLM response missing expected content.")
    except Exception as exc:
        logger.error("Unexpected LLM error: %s", exc)
        raise RuntimeError(f"Unexpected LLM error: {exc}") from exc
