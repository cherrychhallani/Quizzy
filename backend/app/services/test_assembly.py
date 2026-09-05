import random
from typing import List, Optional

from app.database import supabase

# ~1.75 minutes per question, standard JEE/NEET pacing (doc says 1.5-2 min/question)
SECONDS_PER_QUESTION = 105


def fetch_matching_questions(
    document_ids: List[str],
    topics: Optional[List[str]] = None,
    difficulties: Optional[List[str]] = None,
) -> List[dict]:
    query = supabase.table("questions").select("*").in_("document_id", document_ids)
    if topics:
        query = query.in_("topic", topics)
    if difficulties:
        query = query.in_("difficulty", difficulties)
    result = query.execute()
    return result.data or []


def assemble_question_ids(
    questions: List[dict],
    num_questions: Optional[int],
    randomize_order: bool,
) -> List[str]:
    if num_questions is not None and num_questions < len(questions):
        selected = random.sample(questions, num_questions)
    else:
        selected = list(questions)

    if randomize_order:
        random.shuffle(selected)

    return [q["question_id"] for q in selected]


def calculate_time_limit(question_count: int, time_limit_seconds: Optional[int]) -> int:
    if time_limit_seconds is not None:
        return time_limit_seconds
    return question_count * SECONDS_PER_QUESTION