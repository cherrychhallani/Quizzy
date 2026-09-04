import io

import cv2
import fitz  # PyMuPDF
import numpy as np
import pytesseract
from PIL import Image


def extract_with_pymupdf(file_bytes: bytes) -> str:
    """Case A: direct text extraction from a text-based PDF. No OCR involved."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages).strip()


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    """Grayscale -> deskew -> binarize, per the doc's preprocessing step."""
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    coords = np.column_stack(np.where(gray < 255))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = gray.shape[:2]
    matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    deskewed = cv2.warpAffine(
        gray, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    _, binarized = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binarized


def run_ocr(file_bytes: bytes) -> str:
    """Case B: preprocess then OCR with Tesseract (baseline engine)."""
    processed = preprocess_image(file_bytes)
    pil_image = Image.fromarray(processed)
    return pytesseract.image_to_string(pil_image).strip()