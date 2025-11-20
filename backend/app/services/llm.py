import requests
import json
from app.core.config import settings

async def call_llm(messages: list[dict]):
    payload ={
        "model": "deepseek-r1:1.5b",
        "messages": messages,
        "stream": False
    }
    url = f"{settings.ollama_url}/api/chat"
    response = requests.post(url, json=payload)
    data = response.json()
    return data["message"]["content"]