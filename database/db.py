import os
import sqlite3
from contextlib import contextmanager
from config.settings import (
    DB_ENGINE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SSL, DATABASE_PATH
)

def get_ssl_kwargs():
    """Returns SSL connection parameters if enabled or auto-detected for cloud hosts."""
    if DB_SSL in ("true", "1", "yes", "required"):
        return {"ssl": {"check_hostname": False}}
    if DB_SSL == "auto":
        cloud_hosts = ("aivencloud", "tidb", "clever-cloud", "planetscale", "render", "railway")
        if any(ch in DB_HOST.lower() for ch in cloud_hosts):
            return {"ssl": {"check_hostname": False}}
    return {}

try:
    import pymysql
    import pymysql.cursors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

class DictCursorWrapper:
    """Wraps sqlite3.Cursor or pymysql.Cursor for consistent dictionary access & lastrowid."""
    def __init__(self, cursor, is_mysql=False):
        self._cursor = cursor
        self._is_mysql = is_mysql

    def execute(self, sql, params=None):
        if self._is_mysql:
            # Convert SQLite '?' placeholders to MySQL '%s' placeholders
            sql = sql.replace('?', '%s')
            return self._cursor.execute(sql, params or ())
        else:
            # Convert MySQL '%s' placeholders to SQLite '?' placeholders
            sql = sql.replace('%s', '?')
            return self._cursor.execute(sql, params or ())

    def executemany(self, sql, params_list):
        if self._is_mysql:
            sql = sql.replace('?', '%s')
            return self._cursor.executemany(sql, params_list)
        else:
            sql = sql.replace('%s', '?')
            return self._cursor.executemany(sql, params_list)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        return dict(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(r) if not isinstance(r, dict) else r for r in rows]

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

class DBConnectionWrapper:
    """Unified database connection wrapper supporting both MySQL and SQLite."""
    def __init__(self, raw_conn, is_mysql=False):
        self._raw_conn = raw_conn
        self.is_mysql = is_mysql

    def cursor(self):
        if self.is_mysql:
            return DictCursorWrapper(self._raw_conn.cursor(pymysql.cursors.DictCursor), is_mysql=True)
        else:
            return DictCursorWrapper(self._raw_conn.cursor(), is_mysql=False)

    def commit(self):
        self._raw_conn.commit()

    def rollback(self):
        self._raw_conn.rollback()

    def close(self):
        self._raw_conn.close()

def get_connection():
    """Returns an active database connection (MySQL if configured and available, else SQLite)."""
    if DB_ENGINE == "mysql" and MYSQL_AVAILABLE:
        try:
            raw_conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                charset="utf8mb4",
                autocommit=False,
                **get_ssl_kwargs()
            )
            return DBConnectionWrapper(raw_conn, is_mysql=True)
        except Exception as e:
            print(f"Warning: MySQL connection to '{DB_NAME}' failed ({e}). Falling back to SQLite.")

    # SQLite Fallback / Default
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw_conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    raw_conn.row_factory = sqlite3.Row
    raw_conn.execute("PRAGMA foreign_keys = ON")
    raw_conn.execute("PRAGMA journal_mode = WAL")
    return DBConnectionWrapper(raw_conn, is_mysql=False)

@contextmanager
def get_db():
    """Context manager for database operations with automatic commit and error rollback."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes the database schema for the active database engine."""
    if DB_ENGINE == "mysql" and MYSQL_AVAILABLE:
        try:
            from init_mysql import create_mysql_database
            if create_mysql_database():
                return
        except Exception as e:
            print(f"MySQL initialization failed ({e}), falling back to SQLite.")

    # SQLite Schema initialization
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            target_role TEXT DEFAULT 'Software Engineer',
            bio TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER NOT NULL,
            overall_score INTEGER DEFAULT 0,
            summary TEXT,
            technical_skills TEXT,
            soft_skills TEXT,
            education TEXT,
            experience TEXT,
            projects TEXT,
            certifications TEXT,
            missing_sections TEXT,
            strengths TEXT,
            weaknesses TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT DEFAULT '',
            raw_text TEXT NOT NULL,
            parsed_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ats_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER,
            jd_id INTEGER,
            job_title TEXT,
            ats_score INTEGER DEFAULT 0,
            keyword_match_pct INTEGER DEFAULT 0,
            skill_match_pct INTEGER DEFAULT 0,
            experience_match_pct INTEGER DEFAULT 0,
            matching_skills TEXT,
            missing_skills TEXT,
            missing_keywords TEXT,
            formatting_warnings TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            category TEXT DEFAULT 'Technical',
            status TEXT DEFAULT 'Need Improvement',
            proficiency_score INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_role TEXT NOT NULL,
            roadmap_json TEXT NOT NULL,
            is_saved INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            goal_description TEXT DEFAULT '',
            progress_pct INTEGER DEFAULT 0,
            study_hours REAL DEFAULT 0.0,
            completed_lessons INTEGER DEFAULT 0,
            total_lessons INTEGER DEFAULT 10,
            start_date TEXT,
            target_date TEXT,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            doc_type TEXT DEFAULT 'PDF',
            raw_text TEXT NOT NULL,
            summary TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doc_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doc_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (doc_id) REFERENCES uploaded_documents (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            is_pinned INTEGER DEFAULT 0,
            ai_summary TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'Medium',
            category TEXT DEFAULT 'General',
            status TEXT DEFAULT 'Pending',
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            reminder_type TEXT DEFAULT 'Custom',
            due_date TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            job_url TEXT DEFAULT '',
            application_date TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            interview_date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            salary_range TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_role TEXT NOT NULL,
            question_type TEXT DEFAULT 'Technical',
            questions_json TEXT NOT NULL,
            answers_json TEXT DEFAULT '{}',
            evaluation_json TEXT DEFAULT '{}',
            overall_score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)
