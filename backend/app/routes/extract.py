import requests
from fastapi import APIRouter, HTTPException

from app.database import supabase
from app.models import ExtractResponse
from app.services.extraction import extract_with_pymupdf, run_ocr

router = APIRouter()


@router.post("/documents/{document_id}/extract-text", response_model=ExtractResponse)
def extract_text(document_id: str):
    result = supabase.table("documents").select("*").eq("document_id", document_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found.")
    document = result.data[0]

    file_response = requests.get(document["file_url"])
    if file_response.status_code != 200:
        raise HTTPException(status_code=502, detail="Could not download file from storage.")
    file_bytes = file_response.content

    file_type = document["file_type"]
    if file_type == "pdf":
        text = extract_with_pymupdf(file_bytes)          # Case A
    elif file_type in ("jpg", "jpeg", "png"):
        text = run_ocr(file_bytes)                        # Case B
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file_type '{file_type}'.")

    # Known v1 gap from the doc: a scanned worksheet saved as .pdf has no
    # text layer, so PyMuPDF returns empty text here. We don't fall back
    # to OCR yet — that's an accepted limitation for this baseline.
    new_status = "text_extracted" if text else "extraction_empty"

    supabase.table("documents").update(
        {"extracted_text": text, "status": new_status}
    ).eq("document_id", document_id).execute()

    preview = text[:300] + ("..." if len(text) > 300 else "")

    return ExtractResponse(
        document_id=document_id,
        status=new_status,
        char_count=len(text),
        text_preview=preview,
    )