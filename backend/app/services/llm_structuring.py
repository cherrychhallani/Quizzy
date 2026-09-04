from typing import List

from google import genai
from pydantic import ValidationError

from app.config import settings
from app.models import StructuredQuestion, StructuredQuestionList

_client = genai.Client(api_key=settings.gemini_api_key)


def build_prompt(raw_text: str, topics: List[str], retry: bool = False) -> str:
    topic_list_str = ", ".join(topics)

    prompt = f"""You are structuring raw text extracted from a NEET Biology (Class 11)
question paper into individual questions.

Raw extracted text (may have broken line breaks and inconsistent spacing
from OCR or PDF extraction):
---
{raw_text}
---

Instructions:
- Split the text into individual questions.
- For each question, set "type" to "mcq" or "numerical".
- For MCQs, extract all options as a list of strings in "options".
- For numerical questions, set "options" to null.
- Infer "answer" ONLY if it is clearly stated in the text or trivially
  inferable. If it is not clear, set "answer" to null. Never guess with
  false confidence.
- Assign exactly one "topic" per question from this fixed list, using the
  exact spelling given: {topic_list_str}
  If nothing fits well, use "Other".
- Assign a "difficulty": "easy", "medium", or "hard".
- Return ONLY valid JSON matching the required schema. No commentary, no
  markdown code fences, nothing outside the JSON object.
"""

    if retry:
        prompt += "\n\nIMPORTANT: your previous response was not valid JSON matching the schema. Return ONLY the JSON object this time."

    return prompt


def call_gemini(prompt: str) -> str:
    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": StructuredQuestionList.model_json_schema(),
        },
    )
    return response.text


def filter_malformed(questions: List[StructuredQuestion]) -> List[StructuredQuestion]:
    """Lightweight automated validation pass, replacing the manual review step
    the doc deliberately removed from the baseline flow."""
    valid = []
    for q in questions:
        if not q.question_text or not q.question_text.strip():
            continue
        if q.type == "mcq" and (not q.options or len(q.options) < 2):
            continue
        valid.append(q)
    return valid


def structure_text(raw_text: str, topics: List[str]) -> List[StructuredQuestion]:
    for attempt in range(2):  # one automatic retry with a stricter prompt
        prompt = build_prompt(raw_text, topics, retry=(attempt == 1))
        raw_json = call_gemini(prompt)
        try:
            parsed = StructuredQuestionList.model_validate_json(raw_json)
        except (ValidationError, ValueError):
            continue
        return filter_malformed(parsed.questions)

    raise RuntimeError("LLM failed to return valid structured JSON after one retry.")