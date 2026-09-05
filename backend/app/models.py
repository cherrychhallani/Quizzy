from typing import Literal, Optional
from pydantic import BaseModel
from typing import List

class DocumentRecord(BaseModel):
    document_id: str
    user_id: str
    exam: Literal["JEE", "NEET", "OTHER"]
    class_: str
    subject: Optional[str] = None
    file_url: str
    file_type: Literal["pdf", "jpg", "jpeg", "png"]
    status: str
    created_at: str

    class Config:
        populate_by_name = True
        fields = {"class_": "class"}


class UploadResponse(BaseModel):
    document_id: str
    file_url: str
    status: str

class ExtractResponse(BaseModel):
    document_id: str
    status: str
    char_count: int
    text_preview: str

class StructuredQuestion(BaseModel):
    question_text: str
    type: Literal["mcq", "numerical"]
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    topic: str
    difficulty: Literal["easy", "medium", "hard"]


class StructuredQuestionList(BaseModel):
    questions: List[StructuredQuestion]


class StructureResponse(BaseModel):
    document_id: str
    status: str
    question_count: int

class TestConfigRequest(BaseModel):
    user_id: str
    document_ids: List[str]
    num_questions: Optional[int] = None       # None = use all matching questions
    topics: Optional[List[str]] = None
    difficulties: Optional[List[Literal["easy", "medium", "hard"]]] = None
    time_limit_seconds: Optional[int] = None  # None = auto-calculate
    randomize_order: bool = True


class TestSessionResponse(BaseModel):
    session_id: str
    question_ids: List[str]
    time_limit_seconds: int
    status: str

class StartSessionResponse(BaseModel):
    session_id: str
    started_at: str
    time_limit_seconds: int
    status: str


class AnswerUpdateRequest(BaseModel):
    student_answer: Optional[str] = None
    time_delta_seconds: int = 0


class AnswerUpdateResponse(BaseModel):
    question_id: str
    student_answer: Optional[str] = None
    time_spent_seconds: int


class SubmitResponse(BaseModel):
    session_id: str
    status: str
    completed_at: str