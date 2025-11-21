"""Booking field extraction via LLM with a regex safety net."""
import json
import logging
import re
from typing import Any, Dict, Optional

from app.services.llm import call_llm

logger = logging.getLogger(__name__)


EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
TIME_REGEX = re.compile(
    r"\b(?:(?:1[0-2]|0?\d)(?::[0-5]\d)?\s?(?:am|pm)|noon|midnight)\b",
    re.IGNORECASE,
)
WEEKDAY_REGEX = re.compile(
    r"\b(?:next|this|coming)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.IGNORECASE,
)


def _fallback_extract(document_text: str) -> Dict[str, Optional[str]]:
    """Basic regex grab when the LLM reply is missing or broken."""
    email_match = EMAIL_REGEX.search(document_text)
    time_match = TIME_REGEX.search(document_text)
    date_match = WEEKDAY_REGEX.search(document_text)

    name_match = re.search(
        r"(?:my name is|i am|i'm|this is)\s+([A-Za-z][A-Za-z\s\.'-]{0,40})",
        document_text,
        re.IGNORECASE,
    )

    extracted = {
        "name": name_match.group(1).strip() if name_match else None,
        "email": email_match.group(0) if email_match else None,
        "date": date_match.group(0) if date_match else None,
        "time": time_match.group(0) if time_match else None,
    }
    logger.debug("Fallback extractor values: %s", extracted)
    return extracted


def _sanitize_data(data: Dict[str, Any], document_text: str) -> Dict[str, Optional[str]]:
    """Clean noisy fields and keep only values that truly appear in the message."""
    clean_text = re.sub(r"[^a-zA-Z0-9 ]", " ", document_text.lower())

    def _clean_name(name_value: Any) -> Optional[str]:
        if not isinstance(name_value, str):
            return None
        name_value = name_value.strip()
        if not name_value:
            return None
        # Keep only the first line and cut at common sentence punctuation.
        name_value = name_value.splitlines()[0].strip()
        name_value = re.split(r"[.;!?]", name_value)[0].strip()
        # Avoid unreasonably long names that likely captured the full request.
        if len(name_value) > 60:
            name_value = name_value[:60].rsplit(" ", 1)[0].strip()
        if not name_value:
            return None
        # Drop obvious request keywords that indicate we grabbed the whole utterance.
        request_tokens = {"book", "booking", "appointment", "schedule", "meeting", "interview", "reserve"}
        words = set(name_value.lower().split())
        if request_tokens & words:
            return None
        return name_value

    def _clean_value(key: str) -> Optional[str]:
        val = data.get(key)
        if not isinstance(val, str):
            return None
        val = val.strip()
        return val if val else None

    name = _clean_name(data.get("name"))
    email = _clean_value("email")
    date = _clean_value("date")
    time = _clean_value("time")

    if name:
        clean_name = re.sub(r"[^a-zA-Z0-9 ]", " ", name.lower())
        if clean_name not in clean_text:
            logger.debug("Name not confirmed in original text, dropping it")
            name = None

    if email and email not in document_text:
        logger.debug("Email not found in original text, dropping it")
        email = None

    # If the date is actually just a time phrase, drop it and let time capture it.
    if date and TIME_REGEX.fullmatch(date):
        date = None

    # If a time is embedded inside the date, split it out.
    if date:
        embedded_time = TIME_REGEX.search(date)
        if embedded_time:
            if not time:
                time = embedded_time.group(0)
            date = date[: embedded_time.start()].rstrip(" ,.-")
        if date.lower().startswith("at "):
            date = date[3:].lstrip()
        if not date:
            date = None

    # Backfill missing fields from the raw text when possible.
    if not email:
        email_match = EMAIL_REGEX.search(document_text)
        email = email_match.group(0) if email_match else None
    if not time:
        time_match = TIME_REGEX.search(document_text)
        time = time_match.group(0) if time_match else None
    if not date:
        date_match = WEEKDAY_REGEX.search(document_text)
        date = date_match.group(0) if date_match else None

    data["name"] = name
    data["email"] = email
    data["date"] = date
    data["time"] = time
    return data


def _parse_llm_json(raw_answer: str, document_text: str) -> Optional[Dict[str, Optional[str]]]:
    """Find the first JSON object in the LLM reply and sanitize it."""
    blocks = re.findall(r"\{.*?\}", raw_answer, flags=re.DOTALL)
    for block in blocks:
        try:
            data = json.loads(block)
            logger.debug("Parsed booking JSON block: %s", block)
            return _sanitize_data(data, document_text)
        except json.JSONDecodeError as exc:
            logger.info("Could not decode JSON block %s: %s", block, exc)
            continue
    return None


async def extract_booking_info(document_text: str) -> Dict[str, Optional[str]]:
    """Ask the LLM for booking fields; lean on regex fallback if the reply is messy."""
    logger.info("Booking extractor called")

    system_prompt = (
        "You are a strict meeting booking extraction assistant.\\n"
        "\\n"
        "Your ONLY job is to extract 4 fields from the user's message:\\n"
        "- name\\n"
        "- email\\n"
        "- date\\n"
        "- time\\n"
        "\\n"
        "CRITICAL RULES:\\n"
        "1) Every value you output MUST be an exact substring of the user's message.\\n"
        "   - Do NOT invent, modify, or correct names or emails.\\n"
        "   - If the message says 'I am Bibek', the name must be exactly 'Bibek'.\\n"
        "   - If you cannot clearly find the name, set name to null.\\n"
        "\\n"
        "2) A DATE is ANY natural-language phrase that refers to a day or date.\\n"
        "   Examples: 'tomorrow', 'next Friday', 'this coming Monday', 'July 5', 'next Sunday at 3pm'.\\n"
        "   - You must return the date EXACTLY as it appears in the text.\\n"
        "   - Do NOT convert, expand, or interpret dates.\\n"
        "\\n"
        "3) A TIME is ANY time-like phrase.\\n"
        "   Examples: '3pm', '14:30', '10 am', 'noon'.\\n"
        "   - Return it EXACTLY as written.\\n"
        "\\n"
        "4) NEVER compute or infer anything.\\n"
        "   - Do NOT guess names.\\n"
        "   - Do NOT guess emails.\\n"
        "   - Do NOT fix spelling.\\n"
        "   - If a field is not clearly present, set it to null.\\n"
        "\\n"
        "5) Output format:\\n"
        "   You MUST return ONLY a single JSON object, no arrays, no markdown, no explanation.\\n"
        "   It MUST look exactly like this shape:\\n"
        '   {\"name\": ..., \"email\": ..., \"date\": ..., \"time\": ...}\\n'
        "\\n"
        "6) Do NOT wrap the JSON in ```.\\n"
        "7) Do NOT output multiple JSON objects.\\n"
        "8) Do NOT include any text before or after the JSON.\\n"
        "9) Do NOT include ellipses '...' as values; return null when unsure.\\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Extract the booking details from:\\n\\n{document_text}",
        },
    ]

    try:
        raw_answer = await call_llm(messages)
    except Exception as exc:
        logger.warning("Booking extractor LLM call failed: %s", exc)
        return _fallback_extract(document_text)

    logger.debug("Raw extractor output: %s", raw_answer)

    parsed = _parse_llm_json(raw_answer, document_text)
    if parsed:
        return parsed

    logger.info("LLM output unusable, falling back to regex extraction")
    return _sanitize_data(_fallback_extract(document_text), document_text)
