from groq import Groq
import json, os
from models.interview import AnswerEvaluation
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_answer(question, answer, job_description, time_taken, time_limit, difficulty) -> AnswerEvaluation:

    ratio = time_taken / time_limit
    if ratio <= 0.5:     time_score = 10.0
    elif ratio <= 0.8:   time_score = 8.0
    elif ratio <= 1.0:   time_score = 6.0
    else:                time_score = max(0.0, 6.0 - (ratio - 1.0) * 10)

    prompt = f"""You are an expert technical interviewer evaluating a candidate's response.

Job Description: {job_description}
Question (Difficulty: {difficulty}): {question}
Candidate's Answer: {answer}

Evaluate on these 4 dimensions (score each 0.0 to 10.0):
1. accuracy - factually correct?
2. clarity - well-structured and clear?
3. depth - shows deep knowledge?
4. relevance - relevant to question and job?

Respond ONLY in this exact JSON format, no markdown, no extra text:
{{
  "accuracy": 7.5,
  "clarity": 8.0,
  "depth": 6.5,
  "relevance": 7.0,
  "feedback": "1-2 sentence constructive feedback here"
}}"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw = r.choices[0].message.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    composite = (
        data["accuracy"] * 0.35 +
        data["clarity"] * 0.20 +
        data["depth"] * 0.25 +
        data["relevance"] * 0.20
    ) * 0.9 + time_score * 0.1

    return AnswerEvaluation(
        question_id=0,
        accuracy=data["accuracy"],
        clarity=data["clarity"],
        depth=data["depth"],
        relevance=data["relevance"],
        time_efficiency=time_score,
        composite_score=round(composite, 2),
        feedback=data["feedback"]
    )