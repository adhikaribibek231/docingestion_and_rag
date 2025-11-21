import requests
from requests import RequestException

from app.core.config import settings


async def call_llm(messages: list[dict]):
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
        raise RuntimeError(f"LLM request failed: {exc}") from exc
    except KeyError:
        raise RuntimeError("LLM response missing expected content.")
    except Exception as exc:
        raise RuntimeError(f"Unexpected LLM error: {exc}") from exc
