# Hack2Hire: AI Mock Interview Engine

An AI-Powered Mock Interview Platform with Adaptive Scoring, built using FastAPI on the backend and modern vanilla JS/CSS glassmorphism on the frontend. The application utilizes Groq (LLaMA-3.3-70b-versatile model) to dynamically generate interview questions tailored to the candidate's resume and target job description, adjust difficulty adaptively based on answer performance, score answers across multiple dimensions, and generate a final hiring readiness scorecard.

## Key Features
- **PDF Resume Extraction**: Upload a PDF resume to extract content automatically.
- **Adaptive Questions**: Question difficulty changes dynamically (Easy, Medium, Hard) depending on the candidate's answers.
- **Interactive Simulation**: Progresses through questions with a live timer countdown and visual indicators.
- **Multidimensional Scoring**: Automatically scores answers on Accuracy, Clarity, Depth, Relevance, and Time Efficiency.
- **Automatic Early Termination**: Safely halts the interview if consecutive answers show poor performance.
- **Detailed Scorecard**: Generates skill area breakdowns, key strengths/weaknesses, actionable roadmaps, and performance trends.

## Tech Stack
- **Backend**: FastAPI, Uvicorn, Pydantic, python-multipart, PyPDF2
- **LLM/API**: Groq SDK (`llama-3.3-70b-versatile`)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 Glassmorphism with Outfit Google Font

## Getting Started

### Prerequisites
- Python 3.10+
- Groq API Key

### Installation & Setup

1. **Clone/Open the workspace**
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the Application
Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```
Once the server starts, open your browser and navigate to `http://localhost:8000` to interact with the web interface.

---

## Solved Issues & Enhancements

### 1. Fixed Interview Session Overrun Bug
- **Issue**: When an interview finished naturally (reaching the maximum question limit), the session was not marked as finished/terminated in the backend state. This allowed clients to keep sending answer submissions past the question limit, leading to uncontrolled evaluations and incorrect data sizes.
- **Resolution**: Updated `submit_answer` and `get_status` routes in `routers/interview.py` to check both the `is_terminated` flag and if the number of evaluations reached `total_questions`. Any requests submitted after completion now correctly return an HTTP 400 bad request error with `"Interview already ended"`.

### 2. Guarded Against Race Conditions & Out-of-Order Submissions
- **Issue**: Rapid clicking on the submit button or duplicate requests could lead to duplicate evaluations for the same question.
- **Resolution**: Added validation in the `/interview/answer` route to ensure the submitted `question_id` matches the current active `question_number` tracked in the session state.

### 3. Implemented Robust JSON Parser for LLM Outputs
- **Issue**: Standard parsing of the LLM responses was fragile, searching specifically for ` ```json` tags and failing or crashing with a 500 JSONDecodeError if the LLM output contained conversational prefix/suffix text or slightly different formatting.
- **Resolution**: Created a custom `extract_and_parse_json` utility in `utils/helpers.py` that handles various markdown, partial backticks, and floating text formats by isolating curly brace syntax. Integrated this helper across `evaluator.py`, `question_gen.py`, and `report_gen.py` to prevent transient parsing failures.
