from app.services.llm import call_llm
import re
import json


async def extract_booking_info(document_text: str):
    print("DeepSeek extractor called")

    system_prompt = (
        "You are a strict meeting booking extraction assistant.\n"
        "Your rules:\n"
        "1. Extract ONLY these fields: name, email, date, time.\n"
        "2. DO NOT convert dates or times. Return them EXACTLY as written.\n"
        "3. If user says 'tomorrow', 'next Monday', 'Friday morning', etc, "
        "return them AS RAW TEXT.\n"
        "4. NEVER compute actual dates, NEVER rewrite or normalize.\n"
        "5. ALWAYS return ONLY valid JSON with keys: name, email, date, time.\n"
        "6. If any field is missing, set it to null.\n"
        "7. DO NOT add explanations — ONLY return JSON.\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Extract the booking details from:\n\n{document_text}",
        }
    ]

    raw_answer = await call_llm(messages)
    print("RAW DEEPSEEK OUTPUT:", raw_answer)

    # 1) Grab first JSON-looking block
    blocks = re.findall(r'\{[^{}]*\}', raw_answer)
    if not blocks:
        print("Regex FAILED!")
        return {"name": None, "email": None, "date": None, "time": None}

    json_str = blocks[0]
    print("Extracted JSON:", json_str)

    # 2) Parse JSON
    try:
        data = json.loads(json_str)
    except Exception as e:
        print("JSON decode ERROR:", e)
        return {"name": None, "email": None, "date": None, "time": None}

    # 3) VALIDATION: make sure name/email actually appear in original text
    text_lower = document_text.lower()

    name = data.get("name")
    clean_text = re.sub(r'[^a-zA-Z0-9 ]', ' ', document_text.lower())
    clean_name = re.sub(r'[^a-zA-Z0-9 ]', ' ', name.lower()) if name else None

    if clean_name and clean_name not in clean_text:
        print("Name not found in original text (fuzzy check), dropping it.")
        data["name"] = None

    email = data.get("email")
    if email and email not in document_text:
        print("Email not found in original text, dropping it.")
        data["email"] = None

    return data
