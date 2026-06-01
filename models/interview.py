from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    TECHNICAL = "technical"
    CONCEPTUAL = "conceptual"
    BEHAVIORAL = "behavioral"
    SCENARIO = "scenario"

class StartInterviewRequest(BaseModel):
    candidate_name: str
    resume_text: str = Field(..., description="Full resume as plain text")
    job_description: str = Field(..., description="Target job description")
    total_questions: int = Field(default=10, ge=5, le=20)
    time_per_question: int = Field(default=120, description="Seconds per question")

class AnswerSubmission(BaseModel):
    session_id: str
    question_id: int
    answer: str
    time_taken: int = Field(..., description="Seconds taken to answer")

class QuestionResponse(BaseModel):
    session_id: str
    question_id: int
    question: str
    question_type: str
    difficulty: DifficultyLevel
    time_limit: int
    interview_status: str

class AnswerEvaluation(BaseModel):
    question_id: int
    accuracy: float
    clarity: float
    depth: float
    relevance: float
    time_efficiency: float
    composite_score: float
    feedback: str