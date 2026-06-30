// State Management
let currentSession = {
    id: null,
    candidateName: "",
    totalQuestions: 10,
    timeLimitPerQuestion: 120,
    currentQuestionId: 1,
    timeSpentOnCurrent: 0,
    questionsList: []
};

let timerInterval = null;
let secondsRemaining = 0;

// API Configurations
const API_BASE = "/interview";

// DOM Elements
const views = {
    onboarding: document.getElementById('onboarding-view'),
    interview: document.getElementById('interview-view'),
    report: document.getElementById('report-view')
};

const statusBadge = document.getElementById('app-status');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingMessage = document.getElementById('loading-message');

// Onboarding Inputs
const candidateNameInput = document.getElementById('candidate-name');
const resumeFileInput = document.getElementById('resume-file-input');
const resumeDropzone = document.getElementById('resume-dropzone');
const resumeTextarea = document.getElementById('resume-text');
const jdTextarea = document.getElementById('job-description');
const totalQuestionsSlider = document.getElementById('total-questions');
const questionsValueDisplay = document.getElementById('questions-val');
const timeLimitSlider = document.getElementById('time-limit');
const timeValueDisplay = document.getElementById('time-val');
const startBtn = document.getElementById('start-btn');
const fileNameDisplay = document.getElementById('file-name-display');

// Interview Arena Elements
const currentQNumDisplay = document.getElementById('current-q-num');
const totalQNumDisplay = document.getElementById('total-q-num');
const difficultyBadge = document.getElementById('difficulty-badge');
const questionTypeBadge = document.getElementById('question-type-badge');
const questionText = document.getElementById('interview-question');
const candidateAnswerInput = document.getElementById('candidate-answer');
const submitAnswerBtn = document.getElementById('submit-answer-btn');
const charCountDisplay = document.getElementById('char-count');
const logsList = document.getElementById('logs-list');

// Timer Elements
const timerCountdown = document.getElementById('timer-countdown');
const timerProgressRing = document.getElementById('timer-progress-ring');
const strokeDasharray = 2 * Math.PI * 45; // 282.74

// Report Card Elements
const reportCandidateName = document.getElementById('report-candidate-name');
const finalScoreDisplay = document.getElementById('final-score');
const scoreProgressRing = document.getElementById('score-progress-ring');
const badgeCategory = document.getElementById('badge-category');
const badgeReadiness = document.getElementById('badge-readiness');
const skillsListContainer = document.getElementById('skills-list');
const strengthsList = document.getElementById('strengths-list');
const weaknessesList = document.getElementById('weaknesses-list');
const actionableFeedbackList = document.getElementById('actionable-feedback-list');
const performanceTrendBadge = document.getElementById('performance-trend-badge');
const terminationBanner = document.getElementById('termination-banner');
const terminationReason = document.getElementById('termination-reason');
const restartBtn = document.getElementById('restart-btn');

// --- Event Listeners ---

// Initialize Sliders
totalQuestionsSlider.addEventListener('input', (e) => {
    questionsValueDisplay.textContent = e.target.value;
});

timeLimitSlider.addEventListener('input', (e) => {
    timeValueDisplay.textContent = e.target.value + 's';
});

// Character Counter
candidateAnswerInput.addEventListener('input', (e) => {
    charCountDisplay.textContent = e.target.value.length;
});

// Onboarding File Upload Handlers
resumeDropzone.addEventListener('click', () => resumeFileInput.click());

resumeDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    resumeDropzone.classList.add('dragover');
});

resumeDropzone.addEventListener('dragleave', () => {
    resumeDropzone.classList.remove('dragover');
});

resumeDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    resumeDropzone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleResumeFile(files[0]);
    }
});

resumeFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleResumeFile(e.target.files[0]);
    }
});

startBtn.addEventListener('click', startInterview);
submitAnswerBtn.addEventListener('click', () => submitAnswer(false));
restartBtn.addEventListener('click', resetSimulation);

// --- Functions ---

// Switch Views
function showView(viewName) {
    Object.keys(views).forEach(key => {
        if (key === viewName) {
            views[key].classList.add('active');
        } else {
            views[key].classList.remove('active');
        }
    });
}

// Show/Hide Loading Overlay
function toggleLoading(show, message = "Processing...") {
    loadingMessage.textContent = message;
    if (show) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

// Log status updates inside sidebar log
function addLogItem(message) {
    const item = document.createElement('div');
    item.className = 'log-item';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    item.textContent = `[${time}] ${message}`;
    
    // De-activate previous log entries
    const activeLogs = logsList.querySelectorAll('.log-item.active');
    activeLogs.forEach(el => el.classList.remove('active'));
    
    item.classList.add('active');
    logsList.appendChild(item);
    logsList.scrollTop = logsList.scrollHeight;
}

// Handle Resume File Upload & Extraction
async function handleResumeFile(file) {
    if (file.type !== "application/pdf" && !file.name.endsWith('.pdf')) {
        alert("Please upload a PDF file only.");
        return;
    }

    fileNameDisplay.textContent = file.name;
    toggleLoading(true, "Extracting text from PDF resume...");
    statusBadge.textContent = "Parsing Resume";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE}/upload-resume`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to extract text from PDF");
        }

        const data = await response.json();
        resumeTextarea.value = data.extracted_text;
        statusBadge.textContent = "Resume Extracted";
        addLogItem("Resume text extracted successfully");
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
        fileNameDisplay.textContent = "Upload Failed";
        statusBadge.textContent = "Extraction Error";
    } finally {
        toggleLoading(false);
    }
}

// Start Mock Interview Orchestration
async function startInterview() {
    const candidateName = candidateNameInput.value.trim();
    const resumeText = resumeTextarea.value.trim();
    const jobDescription = jdTextarea.value.trim();
    const totalQuestions = parseInt(totalQuestionsSlider.value);
    const timePerQuestion = parseInt(timeLimitSlider.value);

    if (!candidateName) {
        alert("Please enter candidate name.");
        return;
    }
    if (!resumeText) {
        alert("Please paste or extract your resume content.");
        return;
    }
    if (!jobDescription) {
        alert("Please paste the target job description.");
        return;
    }

    toggleLoading(true, "Curating adaptive questions tailored to your profile...");
    statusBadge.textContent = "Preparing Session";

    try {
        const response = await fetch(`${API_BASE}/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                candidate_name: candidateName,
                resume_text: resumeText,
                job_description: jobDescription,
                total_questions: totalQuestions,
                time_per_question: timePerQuestion
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to initialize interview");
        }

        const data = await response.json();
        
        // Save initial state
        currentSession.id = data.session_id;
        currentSession.candidateName = candidateName;
        currentSession.totalQuestions = totalQuestions;
        currentSession.timeLimitPerQuestion = timePerQuestion;
        currentSession.currentQuestionId = data.question_id;
        currentSession.timeSpentOnCurrent = 0;
        
        // Reset inputs and displays
        candidateAnswerInput.value = "";
        charCountDisplay.textContent = "0";
        logsList.innerHTML = "";
        
        // Populate interview components
        currentQNumDisplay.textContent = data.question_id;
        totalQNumDisplay.textContent = totalQuestions;
        renderDifficulty(data.difficulty);
        questionTypeBadge.textContent = data.question_type;
        questionText.textContent = data.question;

        // Set status
        statusBadge.textContent = "Interview Live";
        addLogItem("Interview initialized. Good Luck!");
        addLogItem(`Loaded Question 1 (${data.question_type})`);

        // Swap visual panel
        showView('interview');
        
        // Start countdown timer
        startCountdown(timePerQuestion);

    } catch (e) {
        console.error(e);
        alert(`Failed to launch interview: ${e.message}`);
        statusBadge.textContent = "Launch Failed";
    } finally {
        toggleLoading(false);
    }
}

// Timer loops
function startCountdown(limitSeconds) {
    clearInterval(timerInterval);
    secondsRemaining = limitSeconds;
    currentSession.timeSpentOnCurrent = 0;

    // Reset ring styling
    timerProgressRing.style.strokeDasharray = strokeDasharray;
    updateTimerProgress(1);
    timerCountdown.textContent = secondsRemaining;
    timerProgressRing.className.baseVal = "timer-progress";

    timerInterval = setInterval(() => {
        secondsRemaining--;
        currentSession.timeSpentOnCurrent++;
        timerCountdown.textContent = secondsRemaining;

        const ratio = secondsRemaining / limitSeconds;
        updateTimerProgress(ratio);

        // Shift color thresholds
        if (secondsRemaining <= 15) {
            timerProgressRing.className.baseVal = "timer-progress danger";
        } else if (secondsRemaining <= 45) {
            timerProgressRing.className.baseVal = "timer-progress warning";
        }

        if (secondsRemaining <= 0) {
            clearInterval(timerInterval);
            addLogItem("Time's up! Autosubmitting response...");
            submitAnswer(true);
        }
    }, 1000);
}

function updateTimerProgress(ratio) {
    const offset = strokeDasharray - (ratio * strokeDasharray);
    timerProgressRing.style.strokeDashoffset = offset;
}

function renderDifficulty(level) {
    difficultyBadge.textContent = level.toUpperCase();
    difficultyBadge.className = "";
    if (level === "easy") {
        difficultyBadge.classList.add("badge-easy");
    } else if (level === "medium") {
        difficultyBadge.classList.add("badge-medium");
    } else if (level === "hard") {
        difficultyBadge.classList.add("badge-hard");
    }
}

// Answer Submission
async function submitAnswer(isAutosubmit = false) {
    clearInterval(timerInterval);
    
    const answer = candidateAnswerInput.value.trim() || (isAutosubmit ? "[No response. Time limit exceeded]" : "[Empty response]");
    const timeTaken = currentSession.timeSpentOnCurrent;

    toggleLoading(true, "Evaluating response metrics...");
    statusBadge.textContent = "Scoring Answer";
    addLogItem(`Submitting answer for Question ${currentSession.currentQuestionId}...`);

    try {
        const response = await fetch(`${API_BASE}/answer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: currentSession.id,
                question_id: currentSession.currentQuestionId,
                answer: answer,
                time_taken: timeTaken
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to submit answer");
        }

        const data = await response.json();

        // Check if response is a final report scorecard (ends interview)
        if (data.final_readiness_score !== undefined) {
            renderFinalReport(data);
        } else {
            // Setup next question
            currentSession.currentQuestionId = data.question_id;
            
            candidateAnswerInput.value = "";
            charCountDisplay.textContent = "0";
            
            currentQNumDisplay.textContent = data.question_id;
            renderDifficulty(data.difficulty);
            questionTypeBadge.textContent = data.question_type;
            questionText.textContent = data.question;

            addLogItem(`Answer processed. Feedback recorded.`);
            addLogItem(`Loaded Question ${data.question_id} (${data.question_type}) [Difficulty: ${data.difficulty.toUpperCase()}]`);
            statusBadge.textContent = "Interview Live";

            // Restart timer
            startCountdown(currentSession.timeLimitPerQuestion);
        }

    } catch (e) {
        console.error(e);
        alert(`Error submitting answer: ${e.message}`);
        statusBadge.textContent = "Submission Error";
        // Resume timer where it left off on error
        startCountdown(secondsRemaining);
    } finally {
        toggleLoading(false);
    }
}

// Render final report evaluation
function renderFinalReport(report) {
    statusBadge.textContent = "Evaluation Ready";
    addLogItem("Interview completed. Compilation generated.");
    
    reportCandidateName.textContent = report.candidate_name;
    finalScoreDisplay.textContent = Math.round(report.final_readiness_score);

    // Score ring progress bar
    const scoreCircleDasharray = 2 * Math.PI * 50; // 314.15
    scoreProgressRing.style.strokeDasharray = scoreCircleDasharray;
    const offset = scoreCircleDasharray - ((report.final_readiness_score / 100) * scoreCircleDasharray);
    scoreProgressRing.style.strokeDashoffset = offset;

    // Readiness Category badges
    badgeCategory.textContent = report.readiness_category;
    badgeCategory.className = "badge-category";
    const catClass = report.readiness_category.toLowerCase().replace(" ", "-");
    badgeCategory.classList.add(catClass);

    badgeReadiness.textContent = report.hiring_readiness;
    badgeReadiness.className = "badge-readiness";
    const readClass = report.hiring_readiness.toLowerCase().replace(" ", "-");
    badgeReadiness.classList.add(readClass);

    // Check early termination
    if (report.termination_reason) {
        terminationBanner.style.display = "block";
        terminationReason.textContent = report.termination_reason;
        addLogItem(`Alert: Session terminated early due to: ${report.termination_reason}`);
    } else {
        terminationBanner.style.display = "none";
    }

    // Populate Skill Areas
    skillsListContainer.innerHTML = "";
    report.skill_breakdown.forEach(skill => {
        const row = document.createElement('div');
        row.className = 'skill-row';
        row.innerHTML = `
            <div class="skill-label-row">
                <span class="skill-name">${skill.skill_area}</span>
                <div class="skill-level-score">
                    <span class="skill-level-badge">${skill.level}</span>
                    <span class="skill-score-val">${skill.score}%</span>
                </div>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: 0%"></div>
            </div>
        `;
        skillsListContainer.appendChild(row);
        
        // Trigger width animation frame
        setTimeout(() => {
            row.querySelector('.progress-bar-fill').style.width = `${skill.score}%`;
        }, 100);
    });

    // Populate Strengths
    strengthsList.innerHTML = "";
    report.strengths.forEach(str => {
        const li = document.createElement('li');
        li.textContent = str;
        strengthsList.appendChild(li);
    });

    // Populate Weaknesses
    weaknessesList.innerHTML = "";
    report.weaknesses.forEach(wk => {
        const li = document.createElement('li');
        li.textContent = wk;
        weaknessesList.appendChild(li);
    });

    // Populate Actionable tips
    actionableFeedbackList.innerHTML = "";
    report.actionable_feedback.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        actionableFeedbackList.appendChild(li);
    });

    // Performance Trend badge
    performanceTrendBadge.textContent = report.performance_trend;
    performanceTrendBadge.className = "badge-trend";
    const trendClass = "text-" + report.performance_trend.toLowerCase();
    performanceTrendBadge.classList.add(trendClass);

    showView('report');
}

// Reset state
function resetSimulation() {
    currentSession = {
        id: null,
        candidateName: "",
        totalQuestions: 10,
        timeLimitPerQuestion: 120,
        currentQuestionId: 1,
        timeSpentOnCurrent: 0,
        questionsList: []
    };
    
    candidateNameInput.value = "";
    resumeTextarea.value = "";
    jdTextarea.value = "";
    fileNameDisplay.textContent = "No file selected";
    resumeFileInput.value = "";
    
    statusBadge.textContent = "Ready";
    showView('onboarding');
}
