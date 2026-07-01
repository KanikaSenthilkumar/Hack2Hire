from groq import Groq
import os
from models.interview import DifficultyLevel
from dotenv import load_dotenv
from utils.helpers import extract_and_parse_json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_question(resume_text, job_description, difficulty: DifficultyLevel,
                      asked_questions, question_number, total_questions) -> dict:

    if question_number <= total_questions * 0.4:
        q_type = "technical"
    elif question_number <= total_questions * 0.7:
        q_type = "conceptual or scenario-based"
    else:
        q_type = "behavioral"

    asked_str = "\n".join(asked_questions[-5:]) if asked_questions else "None yet"

    prompt = f"""You are a senior technical interviewer.

Candidate Resume: {resume_text[:1500]}
Job Description: {job_description[:1000]}
Question Number: {question_number} of {total_questions}
Difficulty: {difficulty.value}
Type Needed: {q_type}
Recently Asked (avoid repeating):
{asked_str}

Generate ONE unique interview question matching difficulty and type.

Respond ONLY in this exact JSON format, no markdown, no extra text:
{{
  "question": "Your interview question here?",
  "question_type": "technical",
  "expected_topics": "What a good answer should cover"
}}"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    raw = r.choices[0].message.content

    return extract_and_parse_json(raw)