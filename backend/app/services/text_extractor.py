"""Read PDF or text files and return plain text."""
import logging
from io import BytesIO
from typing import Literal, Optional

import pdfplumber

SupportedFileType = Literal["pdf", "txt"]
logger = logging.getLogger(__name__)


def _detect_file_type(content_type: Optional[str], filename: Optional[str]) -> Optional[SupportedFileType]:
    """Infer file type from content-type header or file extension."""
    if content_type:
        lowered = content_type.lower()
        if "pdf" in lowered:
            return "pdf"
        if "text/plain" in lowered or lowered.startswith("text/"):
            return "txt"

    if filename:
        lowered = filename.lower()
        if lowered.endswith(".pdf"):
            return "pdf"
        if lowered.endswith(".txt"):
            return "txt"
    return None


def _extract_text_from_pdf(contents: bytes) -> str:
    text = []
    buffer = BytesIO(contents)
    try:
        with pdfplumber.open(buffer) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
    except Exception as exc:
        logger.error("Failed to read PDF: %s", exc)
        raise RuntimeError(f"Failed to read PDF: {exc}") from exc
    return "\n".join(text)


def _extract_text_from_txt(contents: bytes) -> str:
    try:
        return contents.decode("utf-8", errors="ignore")
    except Exception as exc:
        logger.error("Failed to decode text file: %s", exc)
        raise RuntimeError(f"Failed to decode text file: {exc}") from exc


def extract_text(contents: bytes, content_type: Optional[str] = None, filename: Optional[str] = None) -> str:
    """Extract text from PDF or TXT; raise if unsupported."""
    file_type = _detect_file_type(content_type, filename)

    if file_type == "pdf":
        return _extract_text_from_pdf(contents)
    if file_type == "txt":
        return _extract_text_from_txt(contents)

    logger.error("Unsupported file type: %s / %s", content_type, filename)
    raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
