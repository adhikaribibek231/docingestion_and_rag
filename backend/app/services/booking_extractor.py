from app.services.llm import call_llm
import re
import json


async def extract_booking_info(document_text: str):
    print("DeepSeek extractor called")

    system_prompt = (
        "You are a strict meeting booking extraction assistant.\n"
        "\n"
        "Your ONLY job is to extract 4 fields from the user's message:\n"
        "- name\n"
        "- email\n"
        "- date\n"
        "- time\n"
        "\n"
        "CRITICAL RULES:\n"
        "1) Every value you output MUST be an exact substring of the user's message.\n"
        "   - Do NOT invent, modify, or correct names or emails.\n"
        "   - If the message says 'I am Bibek', the name must be exactly 'Bibek'.\n"
        "   - If you cannot clearly find the name, set name to null.\n"
        "\n"
        "2) A DATE is ANY natural-language phrase that refers to a day or date.\n"
        "   Examples: 'tomorrow', 'next Friday', 'this coming Monday', 'July 5', 'next Sunday at 3pm'.\n"
        "   - You must return the date EXACTLY as it appears in the text.\n"
        "   - Do NOT convert, expand, or interpret dates.\n"
        "\n"
        "3) A TIME is ANY time-like phrase.\n"
        "   Examples: '3pm', '14:30', '10 am', 'noon'.\n"
        "   - Return it EXACTLY as written.\n"
        "\n"
        "4) NEVER compute or infer anything.\n"
        "   - Do NOT guess names.\n"
        "   - Do NOT guess emails.\n"
        "   - Do NOT fix spelling.\n"
        "   - If a field is not clearly present, set it to null.\n"
        "\n"
        "5) Output format:\n"
        "   You MUST return ONLY a single JSON object, no arrays, no markdown, no explanation.\n"
        "   It MUST look exactly like this shape:\n"
        '   {\"name\": ..., \"email\": ..., \"date\": ..., \"time\": ...}\n'
        "\n"
        "6) Do NOT wrap the JSON in ```.\n"
        "7) Do NOT output multiple JSON objects.\n"
        "8) Do NOT include any text before or after the JSON.\n"
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
