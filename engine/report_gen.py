from groq import Groq
import os
from models.interview import AnswerEvaluation
from models.scoring import FinalReport, SkillScore
from dotenv import load_dotenv
from utils.helpers import extract_and_parse_json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_final_report(candidate_name, resume_text, job_description,
                          evaluations, questions, is_terminated, termination_reason) -> FinalReport:

    if not evaluations:
        return FinalReport(
            candidate_name=candidate_name,
            final_readiness_score=0,
            readiness_category="Needs Improvement",
            hiring_readiness="Not Ready",
            total_questions_asked=0,
            interview_completed=False,
            termination_reason="No answers submitted",
            skill_breakdown=[],
            strengths=[],
            weaknesses=[],
            actionable_feedback=["Please attempt the interview"],
            performance_trend="N/A"
        )

    scores = [e.composite_score for e in evaluations]
    avg = sum(scores) / len(scores)
    readiness_score = round(avg * 10, 1)

    readiness_category = (
        "Strong" if readiness_score >= 75 else
        "Average" if readiness_score >= 50 else
        "Needs Improvement"
    )
    hiring_readiness = (
        "Ready" if readiness_score >= 70 else
        "Borderline" if readiness_score >= 50 else
        "Not Ready"
    )

    if len(scores) >= 3:
        mid = len(scores) // 2
        first = sum(scores[:mid]) / mid
        second = sum(scores[mid:]) / (len(scores) - mid)
        trend = "Improving" if second > first + 0.5 else "Declining" if first > second + 0.5 else "Consistent"
    else:
        trend = "Consistent"

    eval_summary = "\n".join([
        f"Q{i+1}: {q[:80]} | Score: {e.composite_score}/10 | {e.feedback}"
        for i, (q, e) in enumerate(zip(questions, evaluations))
    ])

    prompt = f"""You are a hiring expert generating a candidate interview report.

Candidate: {candidate_name}
Job Description: {job_description[:500]}
Overall Score: {readiness_score}/100
Category: {readiness_category}

Performance:
{eval_summary}

Respond ONLY in this exact JSON format, no markdown, no extra text:
{{
  "skill_breakdown": [
    {{"skill_area": "Python Programming", "score": 75.0, "level": "Strong"}},
    {{"skill_area": "System Design", "score": 60.0, "level": "Average"}},
    {{"skill_area": "Problem Solving", "score": 55.0, "level": "Average"}}
  ],
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "actionable_feedback": ["tip 1", "tip 2", "tip 3"]
}}"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw = r.choices[0].message.content

    data = extract_and_parse_json(raw)

    return FinalReport(
        candidate_name=candidate_name,
        final_readiness_score=readiness_score,
        readiness_category=readiness_category,
        hiring_readiness=hiring_readiness,
        total_questions_asked=len(evaluations),
        interview_completed=not is_terminated,
        termination_reason=termination_reason,
        skill_breakdown=[SkillScore(**s) for s in data["skill_breakdown"]],
        strengths=data["strengths"],
        weaknesses=data["weaknesses"],
        actionable_feedback=data["actionable_feedback"],
        performance_trend=trend
    )