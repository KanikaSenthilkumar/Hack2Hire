
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routers import interview
import traceback

app = FastAPI(
    title="Hack2Hire: AI Interview Engine",
    description="AI-Powered Mock Interview Platform with Adaptive Scoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# This shows EXACT error instead of just "Internal Server Error"
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "trace": traceback.format_exc()}
    )

app.include_router(interview.router)

# Serve the static UI files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
