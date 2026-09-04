import uuid
from datetime import datetime, timezone

import fitz  # PyMuPDF
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.config import settings
from app.database import supabase
from app.models import UploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


def get_extension(filename: str) -> str:
    if "." not in filename:
        raise HTTPException(status_code=400, detail="File has no extension.")
    return filename.rsplit(".", 1)[-1].lower()


def check_pdf_page_count(file_bytes: bytes) -> None:
    """Reject PDFs with more pages than allowed, so a huge file can't break the demo."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not open PDF file — it may be corrupted.")

    page_count = doc.page_count
    doc.close()

    if page_count > settings.max_pdf_pages:
        raise HTTPException(
            status_code=400,
            detail=f"PDF has {page_count} pages; the limit for this baseline is {settings.max_pdf_pages}.",
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    exam: str = Form(...),          # "JEE" | "NEET" | "OTHER"
    student_class: str = Form(..., alias="class"),  # "11" | "12"
    user_id: str = Form(...),       # placeholder until Supabase Auth (OTP) is wired in
):
    # --- Validation ---
    if exam not in {"JEE", "NEET", "OTHER"}:
        raise HTTPException(status_code=400, detail="exam must be JEE, NEET, or OTHER.")
    if student_class not in {"11", "12"}:
        raise HTTPException(status_code=400, detail="class must be 11 or 12.")

    extension = get_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{extension}'. Allowed: pdf, jpg, jpeg, png.",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File content type does not match an allowed type.")

    file_bytes = await file.read()

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {settings.max_file_size_mb}MB limit.",
        )

    if extension == "pdf":
        check_pdf_page_count(file_bytes)

    # --- Upload to Supabase Storage ---
    document_id = str(uuid.uuid4())
    storage_path = f"{user_id}/{document_id}.{extension}"

    try:
        supabase.storage.from_(settings.supabase_storage_bucket).upload(
            storage_path,
            file_bytes,
            {"content-type": file.content_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {e}")

    file_url = supabase.storage.from_(settings.supabase_storage_bucket).get_public_url(storage_path)

    # --- Insert the document record ---
    record = {
        "document_id": document_id,
        "user_id": user_id,
        "exam": exam,
        "class": student_class,
        "file_url": file_url,
        "file_type": "jpeg" if extension == "jpg" else extension,
        "status": "uploaded",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        supabase.table("documents").insert(record).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {e}")

    return UploadResponse(document_id=document_id, file_url=file_url, status="uploaded")
