# 🤖 NexusAI Career & Personal Productivity Assistant

A modern, production-grade **AI Career & Personal Productivity Assistant** SaaS application built with **Python, Streamlit, Google Gemini API, and SQLite**.

---

## ✨ Features Overview

1. **🔒 Secure Authentication & User Isolation**
   - User registration, login, logout, password reset.
   - Salted PBKDF2 password hashing.
   - Complete data isolation per user.

2. **📊 Executive Dashboard**
   - Live KPI cards: Pending tasks, Resume ATS Score, Learning Progress %, Productivity Score.
   - Interactive Plotly charts & task management preview.
   - AI-driven daily career strategy recommendations.

3. **📄 Resume Analyzer & Diagnostic**
   - Multi-format parser (PDF, DOCX, TXT).
   - Structural extraction: Technical & soft skills, education, experience, projects.
   - Quality benchmark gauge (0-100), key strengths, weaknesses, and actionable suggestions.

4. **🎯 ATS Score Checker & Keyword Matcher**
   - Compare resume against any target job description.
   - 0-100 ATS Score with Keyword Match %, Skills Alignment %, and Experience Fit.
   - Identification of missing keywords and ATS formatting warnings.

5. **💼 Job Description Analyzer**
   - Parse requirements, tech stack, salary range, and job mode.
   - Compute candidate compatibility rating (0-100).

6. **🧠 Skill Gap Matrix**
   - Visual category matrix: Mastered, Strong, Need Improvement, Missing.
   - AI prioritization recommendations on what to learn next.

7. **🚀 AI Career Roadmap**
   - 3-Stage learning paths (Foundations, Core Frameworks, Production/DevOps).
   - Milestone practice projects, estimated timelines, and interview topics.

8. **📚 AI Learning Assistant & Tutor**
   - Interactive AI Tutor with code examples and analogies.
   - MCQ Quiz generator with instant feedback.
   - Hands-on coding challenges with starter code and solutions.

9. **📈 Learning Goals Tracker**
   - Track progress %, study hours, and completed lessons.

10. **📑 AI PDF & Document Assistant**
    - Strictly grounded document Q&A.
    - AI summarization, flashcards, and MCQ generation.

11. **📝 Smart Notes Manager**
    - Notes organizer with categories, search, pinning, and AI bullet summarization.

12. **✅ Task Manager & ⚡ AI Daily Schedule**
    - Priority-based task tracking.
    - Time-blocked AI schedule optimizer with Pomodoro recommendations.

13. **⏰ Smart Reminders**
    - Interview, job application, and study session reminders.

14. **📨 AI Email Generator**
    - Job applications, recruiter follow-ups, thank-you notes, networking.
    - Multiple tone presets (Professional, Friendly, Formal, Short, Persuasive).

15. **🎤 AI Mock Interview Coach**
    - Realistic Technical, Behavioral, HR, and Situational questions.
    - 0-100 scoring with strengths, missing concepts, and model answers.

16. **💼 Job Application Pipeline Tracker**
    - Complete Kanban/List pipeline tracking (Saved, Applied, Interview, Offer, Rejected).

17. **💡 Holistic 360° AI Career Insights**
    - Strategic diagnostic aggregating all user data.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.11)
- Google Gemini API Key ([Get free API key](https://aistudio.google.com))

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_PRIMARY_MODEL=gemini-2.0-flash
GEMINI_FALLBACK_MODEL=gemini-1.5-flash
```
*(Note: You can also configure the API Key directly in the UI Settings tab!)*

### 4. Run the Application
```bash
streamlit run app.py
```

---

## 📂 Project Architecture
```
ai_career_assistant/
│
├── app.py                      # Main application runner & router
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment variables
├── README.md                   # Documentation
│
├── config/
│   └── settings.py             # Configuration & constants
│
├── database/
│   ├── db.py                   # SQLite database engine & schema
│   └── models.py               # CRUD operations for all entities
│
├── services/
│   ├── gemini_service.py       # Gemini AI client & JSON extraction
│   ├── resume_service.py       # Resume parsing & scoring
│   ├── ats_service.py          # ATS scoring & keyword matcher
│   ├── job_service.py          # Job description analyzer
│   ├── career_service.py       # Career roadmaps & skill gap
│   ├── learning_service.py     # AI tutor & quizzes
│   ├── pdf_service.py          # Grounded PDF Q&A & summaries
│   ├── productivity_service.py # Daily schedule optimizer
│   ├── email_service.py        # Professional email generator
│   └── interview_service.py    # Mock interview coach & evaluator
│
├── views/
│   ├── auth_view.py            # Login, register, reset password
│   ├── dashboard_view.py       # Dashboard with KPIs & Plotly charts
│   ├── resume_view.py          # Resume analyzer
│   ├── ats_view.py             # ATS checker
│   ├── job_view.py             # Job analyzer
│   ├── skill_gap_view.py       # Skill gap matrix
│   ├── roadmap_view.py         # Career roadmaps
│   ├── learning_tutor_view.py  # Learning tutor
│   ├── learning_tracker_view.py# Learning goals tracker
│   ├── pdf_assistant_view.py   # PDF Q&A assistant
│   ├── notes_view.py           # Smart notes
│   ├── tasks_view.py           # Task manager
│   ├── productivity_view.py    # AI productivity scheduler
│   ├── reminders_view.py       # Reminders
│   ├── email_view.py           # Email generator
│   ├── interview_view.py       # Mock interview coach
│   ├── applications_view.py    # Job application tracker
│   ├── career_insights_view.py # Holistic career insights
│   └── settings_view.py        # Settings & profile
│
├── utils/
│   ├── auth.py                 # Password hashing & session
│   ├── validators.py           # Input validations
│   ├── file_parser.py          # PDF / DOCX / TXT extractor
│   └── ui_components.py        # Reusable UI widgets & cards
│
└── static/
    └── css/
        └── style.css           # Glassmorphism dark cyberpunk theme
```
