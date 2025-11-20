from app.services.llm import call_llm
import re
from datetime import datetime,timezone
import json


async def extract_booking_info(document_text: str):
    print("DeepSeek extractor called")
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict information extraction assistant. "
                "Extract only the NAME, EMAIL, DATE, and TIME for a meeting "
                "from the user's message. "
                "Return the result in valid JSON with keys: "
                "name, email, date, time. "
                "If any field is missing, set it to null."
            ),
        },
        {
            "role": "user",
            "content": f"Extract booking details from the following text:\n\n{document_text}",
        }
    ]
    raw_answer = await call_llm(messages)
    print("RAW DEEPSEEK OUTPUT:", raw_answer)
    print("Applying regex to response...")
    blocks = re.findall(r'\{[^{}]*\}', raw_answer)
    if not blocks:
        print("Regex FAILED to match JSON!")
        return {"name": None, "email": None, "date": None, "time": None}

    json_str = blocks[0]
    print("Extracted JSON:", json_str)

    try:
        data = json.loads(json_str)
    except Exception as e:
        print("JSON decode error:", e)
        return {"name": None, "email": None, "date": None, "time": None}

    return data
