from pydantic import BaseModel
from typing import List, Optional

class SkillScore(BaseModel):
    skill_area: str
    score: float
    level: str

class FinalReport(BaseModel):
    candidate_name: str
    final_readiness_score: float
    readiness_category: str
    hiring_readiness: str
    total_questions_asked: int
    interview_completed: bool
    termination_reason: Optional[str] = None
    skill_breakdown: List[SkillScore]
    strengths: List[str]
    weaknesses: List[str]
    actionable_feedback: List[str]
    performance_trend: str