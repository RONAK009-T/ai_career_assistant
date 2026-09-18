import json
from datetime import datetime
from database.db import get_db

# ----------------- USER CRUD -----------------
def create_user(username, email, password_hash, full_name, target_role="Software Engineer", bio=""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, target_role, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username.strip().lower(), email.strip().lower(), password_hash, full_name.strip(), target_role, bio))
        return cursor.lastrowid

def get_user_by_username(username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_email(email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_user_profile(user_id, full_name, target_role, bio):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET full_name = ?, target_role = ?, bio = ? WHERE id = ?
        """, (full_name.strip(), target_role.strip(), bio.strip(), user_id))
        return cursor.rowcount > 0

def update_user_password(user_id, new_password_hash):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
        return cursor.rowcount > 0

# ----------------- RESUMES & ANALYSES -----------------
def save_resume(user_id, filename, file_type, raw_text):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resumes (user_id, filename, file_type, raw_text)
            VALUES (?, ?, ?, ?)
        """, (user_id, filename, file_type, raw_text))
        return cursor.lastrowid

def get_latest_resume(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def save_resume_analysis(user_id, resume_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resume_analyses (
                user_id, resume_id, overall_score, summary, technical_skills,
                soft_skills, education, experience, projects, certifications,
                missing_sections, strengths, weaknesses, suggestions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, resume_id,
            data.get('overall_score', 0),
            data.get('summary', ''),
            json.dumps(data.get('technical_skills', [])),
            json.dumps(data.get('soft_skills', [])),
            json.dumps(data.get('education', [])),
            json.dumps(data.get('experience', [])),
            json.dumps(data.get('projects', [])),
            json.dumps(data.get('certifications', [])),
            json.dumps(data.get('missing_sections', [])),
            json.dumps(data.get('strengths', [])),
            json.dumps(data.get('weaknesses', [])),
            json.dumps(data.get('suggestions', []))
        ))
        return cursor.lastrowid

def get_latest_resume_analysis(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM resume_analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        for key in ['technical_skills', 'soft_skills', 'education', 'experience', 'projects', 'certifications', 'missing_sections', 'strengths', 'weaknesses', 'suggestions']:
            try:
                res[key] = json.loads(res[key]) if res.get(key) else []
            except Exception:
                res[key] = []
        return res

# ----------------- JOB DESCRIPTIONS & ATS -----------------
def save_job_description(user_id, title, company, raw_text, parsed_json=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_descriptions (user_id, title, company, raw_text, parsed_json)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, company, raw_text, json.dumps(parsed_json) if parsed_json else None))
        return cursor.lastrowid

def save_ats_result(user_id, resume_id, jd_id, job_title, data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ats_results (
                user_id, resume_id, jd_id, job_title, ats_score,
                keyword_match_pct, skill_match_pct, experience_match_pct,
                matching_skills, missing_skills, missing_keywords,
                formatting_warnings, recommendations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, resume_id, jd_id, job_title,
            data.get('ats_score', 0),
            data.get('keyword_match_pct', 0),
            data.get('skill_match_pct', 0),
            data.get('experience_match_pct', 0),
            json.dumps(data.get('matching_skills', [])),
            json.dumps(data.get('missing_skills', [])),
            json.dumps(data.get('missing_keywords', [])),
            json.dumps(data.get('formatting_warnings', [])),
            json.dumps(data.get('recommendations', []))
        ))
        return cursor.lastrowid

def get_latest_ats_result(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ats_results WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        for key in ['matching_skills', 'missing_skills', 'missing_keywords', 'formatting_warnings', 'recommendations']:
            try:
                res[key] = json.loads(res[key]) if res.get(key) else []
            except Exception:
                res[key] = []
        return res

# ----------------- SKILLS & ROADMAPS -----------------
def get_user_skills(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills WHERE user_id = ? ORDER BY proficiency_score DESC", (user_id,))
        return [dict(r) for r in cursor.fetchall()]

def upsert_user_skill(user_id, skill_name, category="Technical", status="Need Improvement", proficiency_score=50):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM skills WHERE user_id = ? AND LOWER(skill_name) = LOWER(?)", (user_id, skill_name))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE skills SET category = ?, status = ?, proficiency_score = ? WHERE id = ?
            """, (category, status, proficiency_score, existing['id']))
            return existing['id']
        else:
            cursor.execute("""
                INSERT INTO skills (user_id, skill_name, category, status, proficiency_score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, skill_name.strip(), category, status, proficiency_score))
            return cursor.lastrowid

def delete_user_skill(skill_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM skills WHERE id = ? AND user_id = ?", (skill_id, user_id))
        return cursor.rowcount > 0

def save_career_roadmap(user_id, target_role, roadmap_data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO career_roadmaps (user_id, target_role, roadmap_json)
            VALUES (?, ?, ?)
        """, (user_id, target_role, json.dumps(roadmap_data)))
        return cursor.lastrowid

def get_latest_career_roadmap(user_id, target_role=None):
    with get_db() as conn:
        cursor = conn.cursor()
        if target_role:
            cursor.execute("SELECT * FROM career_roadmaps WHERE user_id = ? AND target_role = ? ORDER BY created_at DESC LIMIT 1", (user_id, target_role))
        else:
            cursor.execute("SELECT * FROM career_roadmaps WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        try:
            res['roadmap_data'] = json.loads(res['roadmap_json'])
        except Exception:
            res['roadmap_data'] = {}
        return res

# ----------------- LEARNING GOALS -----------------
def get_learning_goals(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_goals WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
        return [dict(r) for r in cursor.fetchall()]

def create_learning_goal(user_id, topic, goal_description, total_lessons=10, start_date=None, target_date=None, notes=""):
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO learning_goals (user_id, topic, goal_description, total_lessons, start_date, target_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, topic.strip(), goal_description.strip(), total_lessons, start_date or now, target_date, notes))
        return cursor.lastrowid

def update_learning_progress(goal_id, user_id, progress_pct, completed_lessons, study_hours, notes=None):
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if notes is not None:
            cursor.execute("""
                UPDATE learning_goals
                SET progress_pct = ?, completed_lessons = ?, study_hours = ?, notes = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (progress_pct, completed_lessons, study_hours, notes, now, goal_id, user_id))
        else:
            cursor.execute("""
                UPDATE learning_goals
                SET progress_pct = ?, completed_lessons = ?, study_hours = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (progress_pct, completed_lessons, study_hours, now, goal_id, user_id))
        return cursor.rowcount > 0

def delete_learning_goal(goal_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_goals WHERE id = ? AND user_id = ?", (goal_id, user_id))
        return cursor.rowcount > 0

# ----------------- UPLOADED DOCUMENTS & CHAT -----------------
def save_uploaded_document(user_id, filename, doc_type, raw_text, summary=""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO uploaded_documents (user_id, filename, doc_type, raw_text, summary)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, filename, doc_type, raw_text, summary))
        return cursor.lastrowid

def get_user_documents(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, doc_type, summary, created_at FROM uploaded_documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return [dict(r) for r in cursor.fetchall()]

def get_document_by_id(doc_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uploaded_documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_document(doc_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uploaded_documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
        return cursor.rowcount > 0

def save_doc_chat_message(user_id, doc_id, role, message):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO doc_chat_history (user_id, doc_id, role, message)
            VALUES (?, ?, ?, ?)
        """, (user_id, doc_id, role, message))
        return cursor.lastrowid

def get_doc_chat_history(doc_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, message, created_at FROM doc_chat_history
            WHERE doc_id = ? AND user_id = ? ORDER BY id ASC
        """, (doc_id, user_id))
        return [dict(r) for r in cursor.fetchall()]

# ----------------- NOTES -----------------
def get_notes(user_id, category=None, search_query=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM notes WHERE user_id = ?"
        params = [user_id]
        if category and category != 'All':
            query += " AND category = ?"
            params.append(category)
        if search_query:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        query += " ORDER BY is_pinned DESC, updated_at DESC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

def create_note(user_id, title, content, category="General", is_pinned=0, ai_summary=""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (user_id, title, content, category, is_pinned, ai_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title.strip(), content.strip(), category, 1 if is_pinned else 0, ai_summary))
        return cursor.lastrowid

def update_note(note_id, user_id, title, content, category, is_pinned, ai_summary=None):
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if ai_summary is not None:
            cursor.execute("""
                UPDATE notes SET title = ?, content = ?, category = ?, is_pinned = ?, ai_summary = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (title.strip(), content.strip(), category, 1 if is_pinned else 0, ai_summary, now, note_id, user_id))
        else:
            cursor.execute("""
                UPDATE notes SET title = ?, content = ?, category = ?, is_pinned = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (title.strip(), content.strip(), category, 1 if is_pinned else 0, now, note_id, user_id))
        return cursor.rowcount > 0

def delete_note(note_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        return cursor.rowcount > 0

# ----------------- TASKS -----------------
def get_tasks(user_id, status=None, priority=None, category=None, search_query=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM tasks WHERE user_id = ?"
        params = [user_id]
        if status and status != 'All':
            query += " AND status = ?"
            params.append(status)
        if priority and priority != 'All':
            query += " AND priority = ?"
            params.append(priority)
        if category and category != 'All':
            query += " AND category = ?"
            params.append(category)
        if search_query:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        query += " ORDER BY CASE priority WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, due_date ASC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

def create_task(user_id, title, description="", priority="Medium", category="General", status="Pending", due_date=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, priority, category, status, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title.strip(), description.strip(), priority, category, status, due_date))
        return cursor.lastrowid

def update_task(task_id, user_id, title, description, priority, category, status, due_date):
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE tasks SET title = ?, description = ?, priority = ?, category = ?, status = ?, due_date = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (title.strip(), description.strip(), priority, category, status, due_date, now, task_id, user_id))
        return cursor.rowcount > 0

def delete_task(task_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        return cursor.rowcount > 0

# ----------------- REMINDERS -----------------
def get_reminders(user_id, reminder_type=None, is_completed=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM reminders WHERE user_id = ?"
        params = [user_id]
        if reminder_type and reminder_type != 'All':
            query += " AND reminder_type = ?"
            params.append(reminder_type)
        if is_completed is not None:
            query += " AND is_completed = ?"
            params.append(1 if is_completed else 0)
        query += " ORDER BY due_date ASC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

def create_reminder(user_id, title, reminder_type="Custom", due_date="", notes=""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (user_id, title, reminder_type, due_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title.strip(), reminder_type, due_date, notes.strip()))
        return cursor.lastrowid

def toggle_reminder(reminder_id, user_id, is_completed):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET is_completed = ? WHERE id = ? AND user_id = ?", (1 if is_completed else 0, reminder_id, user_id))
        return cursor.rowcount > 0

def delete_reminder(reminder_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
        return cursor.rowcount > 0

# ----------------- JOB APPLICATIONS -----------------
def get_job_applications(user_id, status=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM job_applications WHERE user_id = ?"
        params = [user_id]
        if status and status != 'All':
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY application_date DESC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

def create_job_application(user_id, company, position, job_url="", application_date="", status="Applied", interview_date="", notes="", salary_range=""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_applications (user_id, company, position, job_url, application_date, status, interview_date, notes, salary_range)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, company.strip(), position.strip(), job_url.strip(), application_date, status, interview_date, notes.strip(), salary_range.strip()))
        return cursor.lastrowid

def update_job_application(app_id, user_id, company, position, job_url, application_date, status, interview_date, notes, salary_range):
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE job_applications
            SET company = ?, position = ?, job_url = ?, application_date = ?, status = ?, interview_date = ?, notes = ?, salary_range = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (company.strip(), position.strip(), job_url.strip(), application_date, status, interview_date, notes.strip(), salary_range.strip(), now, app_id, user_id))
        return cursor.rowcount > 0

def delete_job_application(app_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_applications WHERE id = ? AND user_id = ?", (app_id, user_id))
        return cursor.rowcount > 0

# ----------------- INTERVIEW SESSIONS -----------------
def save_interview_session(user_id, target_role, question_type, questions_list, answers_dict=None, evaluation_data=None, score=0):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interview_sessions (
                user_id, target_role, question_type, questions_json, answers_json, evaluation_json, overall_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, target_role, question_type,
            json.dumps(questions_list),
            json.dumps(answers_dict or {}),
            json.dumps(evaluation_data or {}),
            score
        ))
        return cursor.lastrowid

def get_latest_interview_session(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interview_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        for key in ['questions_json', 'answers_json', 'evaluation_json']:
            try:
                res[key] = json.loads(res[key])
            except Exception:
                res[key] = {}
        return res
