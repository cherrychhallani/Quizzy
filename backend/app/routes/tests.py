import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import supabase
from app.models import (
    TestConfigRequest,
    TestSessionResponse,
    StartSessionResponse,
    AnswerUpdateRequest,
    AnswerUpdateResponse,
    SubmitResponse,
)
from app.services.test_assembly import (
    assemble_question_ids,
    calculate_time_limit,
    fetch_matching_questions,
)
from app.services.test_session import is_within_time_limit

router = APIRouter()


@router.post("/tests", response_model=TestSessionResponse)
def create_test_session(config: TestConfigRequest):
    questions = fetch_matching_questions(
        document_ids=config.document_ids,
        topics=config.topics,
        difficulties=config.difficulties,
    )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="No questions match the given document(s), topic(s), and difficulty filter.",
        )

    if config.num_questions is not None and config.num_questions <= 0:
        raise HTTPException(status_code=400, detail="num_questions must be a positive integer.")

    question_ids = assemble_question_ids(
        questions=questions,
        num_questions=config.num_questions,
        randomize_order=config.randomize_order,
    )

    time_limit_seconds = calculate_time_limit(len(question_ids), config.time_limit_seconds)

    session_id = str(uuid.uuid4())
    record = {
        "session_id": session_id,
        "user_id": config.user_id,
        "question_ids": question_ids,
        "time_limit_seconds": time_limit_seconds,
        "status": "not_started",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    supabase.table("test_sessions").insert(record).execute()

    return TestSessionResponse(
        session_id=session_id,
        question_ids=question_ids,
        time_limit_seconds=time_limit_seconds,
        status="not_started",
    )

@router.post("/tests/{session_id}/start", response_model=StartSessionResponse)
def start_test_session(session_id: str):
    result = supabase.table("test_sessions").select("*").eq("session_id", session_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Test session not found.")
    session = result.data[0]

    if session["status"] in ("completed", "expired"):
        raise HTTPException(
            status_code=400,
            detail=f"This session is already '{session['status']}' and cannot be restarted.",
        )

    if session["started_at"] is None:
        started_at = datetime.now(timezone.utc).isoformat()
        supabase.table("test_sessions").update(
            {"started_at": started_at, "status": "in_progress"}
        ).eq("session_id", session_id).execute()
    else:
        # Already started earlier (e.g. page refresh) — resume, don't reset the clock.
        started_at = session["started_at"]

    return StartSessionResponse(
        session_id=session_id,
        started_at=started_at,
        time_limit_seconds=session["time_limit_seconds"],
        status="in_progress",
    )


@router.patch("/tests/{session_id}/answers/{question_id}", response_model=AnswerUpdateResponse)
def autosave_answer(session_id: str, question_id: str, payload: AnswerUpdateRequest):
    session_result = supabase.table("test_sessions").select("*").eq("session_id", session_id).execute()
    if not session_result.data:
        raise HTTPException(status_code=404, detail="Test session not found.")
    session = session_result.data[0]

    if session["status"] != "in_progress":
        raise HTTPException(status_code=400, detail=f"Session status is '{session['status']}'; cannot autosave.")

    existing = (
        supabase.table("answers")
        .select("*")
        .eq("session_id", session_id)
        .eq("question_id", question_id)
        .execute()
    )

    if existing.data:
        current = existing.data[0]
        new_time_spent = current["time_spent_seconds"] + payload.time_delta_seconds
        update_fields = {
            "time_spent_seconds": new_time_spent,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if payload.student_answer is not None:
            update_fields["student_answer"] = payload.student_answer

        supabase.table("answers").update(update_fields).eq("session_id", session_id).eq(
            "question_id", question_id
        ).execute()
        student_answer = update_fields.get("student_answer", current["student_answer"])
    else:
        new_time_spent = payload.time_delta_seconds
        record = {
            "answer_id": str(uuid.uuid4()),
            "session_id": session_id,
            "question_id": question_id,
            "student_answer": payload.student_answer,
            "time_spent_seconds": new_time_spent,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        supabase.table("answers").insert(record).execute()
        student_answer = payload.student_answer

    return AnswerUpdateResponse(
        question_id=question_id,
        student_answer=student_answer,
        time_spent_seconds=new_time_spent,
    )


@router.post("/tests/{session_id}/submit", response_model=SubmitResponse)
def submit_test_session(session_id: str):
    result = supabase.table("test_sessions").select("*").eq("session_id", session_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Test session not found.")
    session = result.data[0]

    if session["status"] != "in_progress":
        raise HTTPException(status_code=400, detail=f"Session status is '{session['status']}'; cannot submit.")

    if session["started_at"] is None:
        raise HTTPException(status_code=400, detail="Session was never started.")

    if not is_within_time_limit(session["started_at"], session["time_limit_seconds"]):
        supabase.table("test_sessions").update({"status": "expired"}).eq("session_id", session_id).execute()
        raise HTTPException(
            status_code=403,
            detail="Time limit exceeded — this session cannot be submitted.",
        )

    completed_at = datetime.now(timezone.utc).isoformat()
    supabase.table("test_sessions").update(
        {"status": "completed", "completed_at": completed_at}
    ).eq("session_id", session_id).execute()

    return SubmitResponse(session_id=session_id, status="completed", completed_at=completed_at)