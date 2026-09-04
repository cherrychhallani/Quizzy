import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import supabase
from app.models import StructureResponse
from app.services.llm_structuring import structure_text
from app.topics import NEET_BIOLOGY_CLASS_11_TOPICS

router = APIRouter()


@router.post("/documents/{document_id}/structure", response_model=StructureResponse)
def structure_document(document_id: str):
    result = supabase.table("documents").select("*").eq("document_id", document_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found.")
    document = result.data[0]

    if document["status"] != "text_extracted":
        raise HTTPException(
            status_code=400,
            detail=f"Document status is '{document['status']}'; text must be extracted first.",
        )

    raw_text = document.get("extracted_text")
    if not raw_text:
        raise HTTPException(status_code=400, detail="No extracted text available for this document.")

    # v1 scope: only NEET Class 11 (Biology) has a topic list wired in.
    if document["exam"] != "NEET" or document["class"] != "11":
        raise HTTPException(
            status_code=400,
            detail="Structuring currently only supports NEET, Class 11 (Biology).",
        )

    try:
        questions = structure_text(raw_text, NEET_BIOLOGY_CLASS_11_TOPICS)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if not questions:
        supabase.table("documents").update(
            {"status": "structuring_failed"}
        ).eq("document_id", document_id).execute()
        return StructureResponse(document_id=document_id, status="structuring_failed", question_count=0)

    rows = [
        {
            "question_id": str(uuid.uuid4()),
            "document_id": document_id,
            "question_text": q.question_text,
            "type": q.type,
            "options": q.options,
            "answer": q.answer,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        for q in questions
    ]

    supabase.table("questions").insert(rows).execute()
    supabase.table("documents").update({"status": "structured"}).eq("document_id", document_id).execute()

    return StructureResponse(document_id=document_id, status="structured", question_count=len(questions))