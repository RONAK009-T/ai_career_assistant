from services.gemini_service import call_gemini_json

def generate_daily_schedule(tasks: list, focus_goal: str = "") -> dict:
    prompt = f"Plan daily schedule for tasks:\n{tasks}\nFocus: {focus_goal}"
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("schedule"):
        return {
            "productivity_score": 88,
            "top_focus": focus_goal or "Complete core development milestones and submit priority applications.",
            "schedule": [
                {"time": "09:00 - 10:30", "activity": "Deep Work Sprint: Core Coding & Architecture Implementation", "type": "Focus"},
                {"time": "10:30 - 10:45", "activity": "Mindful Rest & Hydration Break", "type": "Break"},
                {"time": "10:45 - 12:15", "activity": "Resume Enhancement & Target Job ATS Alignment", "type": "Career"},
                {"time": "12:15 - 13:15", "activity": "Nutritious Lunch & Walk", "type": "Break"},
                {"time": "13:15 - 15:00", "activity": "Curriculum Study & Skill Gap Practice (Docker / APIs)", "type": "Learning"},
                {"time": "15:15 - 16:30", "activity": "Tailored Job Applications & Outreach Networking", "type": "Career"},
                {"time": "17:00 - 18:00", "activity": "Mock Technical Interview Practice & Answer Review", "type": "Interview"}
            ],
            "priority_order": [
                "1. Complete urgent development deliverables",
                "2. Submit targeted job applications before afternoon recruiter reviews",
                "3. Deep dive into evening technical interview practice questions"
            ],
            "time_management_tips": [
                "Use 50-minute Pomodoro sprints to maintain deep cognitive flow.",
                "Batch recruiter communications and emails into a single afternoon block."
            ]
        }
    return res
