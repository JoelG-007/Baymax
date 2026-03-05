import pdfplumber
import pytesseract
from PIL import Image
import io


def extract_text(file):
    """
    Extracts text from either a PDF or an image file (JPG, PNG).
    Routes to the correct extractor based on file type.
    """
    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return _extract_from_pdf(file)
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        return _extract_from_image(file)
    else:
        return ""


def _extract_from_pdf(file):
    """Extracts text from a PDF using pdfplumber."""
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def _extract_from_image(file):
    """Extracts text from an image using Tesseract OCR."""
    try:
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        return text
    except Exception:
        return ""