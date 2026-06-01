from fastapi import APIRouter, HTTPException
from models.interview import StartInterviewRequest, AnswerSubmission, QuestionResponse, DifficultyLevel
from models.scoring import FinalReport
from engine.question_gen import generate_question
from engine.evaluator import evaluate_answer
from engine.adaptive import get_next_difficulty, should_terminate, update_consecutive_low
from engine.report_gen import generate_final_report
import uuid

router = APIRouter(prefix="/interview", tags=["Interview"])
sessions = {}

@router.post("/start")
async def start_interview(request: StartInterviewRequest):
    session_id = str(uuid.uuid4())
    q_data = generate_question(
        request.resume_text, request.job_description,
        DifficultyLevel.EASY, [], 1, request.total_questions
    )
    sessions[session_id] = {
        "candidate_name": request.candidate_name,
        "resume_text": request.resume_text,
        "job_description": request.job_description,
        "total_questions": request.total_questions,
        "time_per_question": request.time_per_question,
        "current_question_number": 1,
        "current_difficulty": DifficultyLevel.EASY,
        "evaluations": [],
        "questions": [q_data["question"]],
        "is_terminated": False,
        "termination_reason": None,
        "consecutive_low_scores": 0
    }
    return {
        "session_id": session_id,
        "question_id": 1,
        "question": q_data["question"],
        "question_type": q_data["question_type"],
        "difficulty": DifficultyLevel.EASY,
        "time_limit": request.time_per_question,
        "interview_status": "ongoing"
    }

@router.post("/answer")
async def submit_answer(submission: AnswerSubmission):
    session = sessions.get(submission.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["is_terminated"]:
        raise HTTPException(status_code=400, detail="Interview already ended")

    evaluation = evaluate_answer(
        question=session["questions"][-1],
        answer=submission.answer,
        job_description=session["job_description"],
        time_taken=submission.time_taken,
        time_limit=session["time_per_question"],
        difficulty=session["current_difficulty"].value
    )
    evaluation.question_id = submission.question_id
    session["evaluations"].append(evaluation)

    session["consecutive_low_scores"] = update_consecutive_low(
        session["consecutive_low_scores"], evaluation.composite_score
    )
    terminate, reason = should_terminate(
        evaluation.composite_score, session["consecutive_low_scores"]
    )

    q_num = session["current_question_number"]
    total = session["total_questions"]

    if terminate or q_num >= total:
        session["is_terminated"] = terminate
        session["termination_reason"] = reason if terminate else None
        return generate_final_report(
            session["candidate_name"], session["resume_text"],
            session["job_description"], session["evaluations"],
            session["questions"], terminate, reason
        )

    next_diff = get_next_difficulty(session["current_difficulty"], evaluation.composite_score)
    session["current_difficulty"] = next_diff
    session["current_question_number"] += 1

    next_q = generate_question(
        session["resume_text"], session["job_description"],
        next_diff, session["questions"],
        session["current_question_number"], total
    )
    session["questions"].append(next_q["question"])

    return {
        "session_id": submission.session_id,
        "question_id": session["current_question_number"],
        "question": next_q["question"],
        "question_type": next_q["question_type"],
        "difficulty": next_diff,
        "time_limit": session["time_per_question"],
        "interview_status": "ongoing"
    }

@router.get("/status/{session_id}")
async def get_status(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "candidate_name": session["candidate_name"],
        "current_question": session["current_question_number"],
        "total_questions": session["total_questions"],
        "current_difficulty": session["current_difficulty"],
        "is_terminated": session["is_terminated"],
        "questions_answered": len(session["evaluations"])
    }

@router.get("/report/{session_id}")
async def get_report(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return generate_final_report(
        session["candidate_name"], session["resume_text"],
        session["job_description"], session["evaluations"],
        session["questions"], session["is_terminated"],
        session["termination_reason"]
    )