import pdfplumber
from io import BytesIO

def extract_text_from_pdf(contents):
    
    try:
        text = []
        buffer = BytesIO(contents)
        with pdfplumber.open(buffer) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    except FileNotFoundError:
        return "Error: The specified file was not found."
    except Exception as e:
        return f"Error: could not extract text due to {str(e)}"