import sqlite3
import hashlib
from pathlib import Path


def init_db(app):
    """Create necessary tables in the SQLite database."""
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS first_login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS onboarding_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                department TEXT NOT NULL,
                problem_solving INTEGER NOT NULL,
                resume_ready INTEGER NOT NULL,
                interview_ready INTEGER NOT NULL,
                consistency INTEGER NOT NULL,
                overall_score REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS skill_checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mock_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                test_name TEXT NOT NULL,
                source TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL NOT NULL,
                date_taken TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_content TEXT,
                analysis_data TEXT,
                ats_score REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#FF6B35',
                position INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                log_date TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                UNIQUE(habit_id, log_date),
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                context TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                uploader_name TEXT NOT NULL,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                branch TEXT NOT NULL,
                year_of_engineering TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                description TEXT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                file_size INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TEXT,
                reviewed_by TEXT
            )
            """
        )
        # Backfill schema for existing databases.
        res_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(resources)").fetchall()
        }
        if "file_hash" not in res_columns:
            conn.execute("ALTER TABLE resources ADD COLUMN file_hash TEXT")
        if "file_size" not in res_columns:
            conn.execute("ALTER TABLE resources ADD COLUMN file_size INTEGER")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_resources_file_hash ON resources(file_hash)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resource_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL,
                commenter_email TEXT NOT NULL,
                commenter_name TEXT NOT NULL,
                comment TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_refinements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                summary TEXT,
                questions_data TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
def get_connection(db_path):
    """Return a sqlite3 connection with Row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_email(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cur.fetchone()


def create_user(db_path, full_name, email, password_hash):
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            (full_name, email, password_hash),
        )
        conn.commit()


def update_user_password(db_path, email, password_hash):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (password_hash, email),
        )
        conn.commit()


def get_first_login_record(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM first_login WHERE email = ?", (email,))
        return cur.fetchone()


def ensure_first_login_record(db_path, email):
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO first_login (email, completed) VALUES (?, 0)",
            (email,),
        )
        conn.commit()


def set_first_login_completed(db_path, email):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE first_login SET completed = 1, updated_at = datetime('now') WHERE email = ?",
            (email,),
        )
        conn.commit()


def save_onboarding_response(
    db_path,
    email,
    department,
    problem_solving,
    resume_ready,
    interview_ready,
    consistency,
    overall_score,
):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO onboarding_responses
            (email, department, problem_solving, resume_ready, interview_ready, consistency, overall_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email,
                department,
                problem_solving,
                resume_ready,
                interview_ready,
                consistency,
                overall_score,
            ),
        )
        conn.commit()


def get_onboarding_response(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM onboarding_responses WHERE email = ?", (email,))
        return cur.fetchone()


def get_skill_checklist(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT data FROM skill_checklists WHERE email = ?", (email,))
        row = cur.fetchone()
        return row["data"] if row else None


def save_skill_checklist(db_path, email, data):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO skill_checklists (email, data, updated_at)
            VALUES (?, ?, datetime('now'))
            """,
            (email, data),
        )
        conn.commit()


def create_mock_test(db_path, email, test_name, source, score, max_score, date_taken, notes):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO mock_tests
            (email, test_name, source, score, max_score, date_taken, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (email, test_name, source, score, max_score, date_taken, notes),
        )
        conn.commit()
        return cur.lastrowid


def list_mock_tests(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT * FROM mock_tests
            WHERE email = ?
            ORDER BY date_taken DESC, created_at DESC
            """,
            (email,),
        )
        return cur.fetchall()


def update_mock_test(db_path, test_id, email, test_name, source, score, max_score, date_taken, notes):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE mock_tests
            SET test_name = ?,
                source = ?,
                score = ?,
                max_score = ?,
                date_taken = ?,
                notes = ?,
                updated_at = datetime('now')
            WHERE id = ? AND email = ?
            """,
            (test_name, source, score, max_score, date_taken, notes, test_id, email),
        )
        conn.commit()
        return cur.rowcount


def delete_mock_test(db_path, test_id, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM mock_tests WHERE id = ? AND email = ?",
            (test_id, email),
        )
        conn.commit()
        return cur.rowcount


def save_resume(db_path, email, filename, file_path, file_content):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO resumes (email, filename, file_path, file_content)
            VALUES (?, ?, ?, ?)
            """,
            (email, filename, file_path, file_content),
        )
        conn.commit()
        return cur.lastrowid


def get_latest_resume(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT * FROM resumes
            WHERE email = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (email,),
        )
        return cur.fetchone()


def update_resume_analysis(db_path, resume_id, analysis_data, ats_score):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            UPDATE resumes
            SET analysis_data = ?,
                ats_score = ?,
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (analysis_data, ats_score, resume_id),
        )
        conn.commit()


def get_resume_by_id(db_path, resume_id, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM resumes WHERE id = ? AND email = ?",
            (resume_id, email),
        )
        return cur.fetchone()


def list_resumes(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT id, filename, ats_score, created_at
            FROM resumes
            WHERE email = ?
            ORDER BY created_at DESC
            """,
            (email,),
        )
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Habits / Progress Tracker
# ─────────────────────────────────────────────────────────────────────────────


def create_habit(db_path, email, name, color="#FF6B35"):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM habits WHERE email = ?",
            (email,),
        )
        position = cur.fetchone()[0]
        cur = conn.execute(
            "INSERT INTO habits (email, name, color, position) VALUES (?, ?, ?, ?)",
            (email, name, color, position),
        )
        conn.commit()
        return cur.lastrowid


def list_habits(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM habits WHERE email = ? ORDER BY position ASC",
            (email,),
        )
        return cur.fetchall()


def update_habit(db_path, habit_id, email, name, color):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "UPDATE habits SET name = ?, color = ? WHERE id = ? AND email = ?",
            (name, color, habit_id, email),
        )
        conn.commit()
        return cur.rowcount


def delete_habit(db_path, habit_id, email):
    with get_connection(db_path) as conn:
        conn.execute(
            "DELETE FROM habit_logs WHERE habit_id = ? AND email = ?",
            (habit_id, email),
        )
        conn.execute(
            "DELETE FROM habits WHERE id = ? AND email = ?",
            (habit_id, email),
        )
        conn.commit()
        return 1


def toggle_habit_log(db_path, habit_id, email, log_date, done):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO habit_logs (habit_id, email, log_date, done)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (habit_id, email, log_date, done),
        )
        conn.commit()


def get_habit_logs(db_path, email, year, month):
    with get_connection(db_path) as conn:
        prefix = f"{year:04d}-{month:02d}"
        cur = conn.execute(
            """
            SELECT hl.habit_id, hl.log_date, hl.done
            FROM habit_logs hl
            JOIN habits h ON h.id = hl.habit_id
            WHERE hl.email = ? AND hl.log_date LIKE ?
            ORDER BY hl.log_date
            """,
            (email, f"{prefix}%"),
        )
        return cur.fetchall()


def get_leaderboard(db_path):
    """
    Compute per-user best streak and current streak across ALL habits.
    A "streak day" = a day where the user completed at least one habit.
    Returns list of dicts sorted by best_streak desc.
    """
    with get_connection(db_path) as conn:
        # Get all distinct (email, log_date) where at least one habit was done
        cur = conn.execute(
            """
            SELECT DISTINCT hl.email, hl.log_date
            FROM habit_logs hl
            WHERE hl.done = 1
            ORDER BY hl.email, hl.log_date
            """
        )
        rows = cur.fetchall()

    from datetime import datetime, timedelta

    # Group dates by user
    user_dates = {}
    for row in rows:
        email = row["email"]
        if email not in user_dates:
            user_dates[email] = []
        user_dates[email].append(row["log_date"])

    # Get display names
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT email, full_name FROM users")
        name_map = {r["email"]: r["full_name"] for r in cur.fetchall()}

    # Get habit counts per user
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT email, COUNT(*) as cnt FROM habits GROUP BY email"
        )
        habit_counts = {r["email"]: r["cnt"] for r in cur.fetchall()}

    today_str = datetime.now().strftime("%Y-%m-%d")
    results = []

    for email, dates in user_dates.items():
        sorted_dates = sorted(set(dates))
        if not sorted_dates:
            continue

        # Convert to date objects
        date_objs = []
        for ds in sorted_dates:
            try:
                date_objs.append(datetime.strptime(ds, "%Y-%m-%d").date())
            except ValueError:
                continue

        best_streak = 1
        current_streak = 1
        streak = 1

        for i in range(1, len(date_objs)):
            if (date_objs[i] - date_objs[i - 1]).days == 1:
                streak += 1
            else:
                streak = 1
            if streak > best_streak:
                best_streak = streak

        # Current streak: count backwards from today/yesterday
        today_date = datetime.now().date()
        if date_objs[-1] == today_date or date_objs[-1] == today_date - timedelta(days=1):
            current_streak = 1
            for i in range(len(date_objs) - 2, -1, -1):
                if (date_objs[i + 1] - date_objs[i]).days == 1:
                    current_streak += 1
                else:
                    break
        else:
            current_streak = 0

        results.append({
            "email": email,
            "name": name_map.get(email, email.split("@")[0]),
            "best_streak": best_streak,
            "current_streak": current_streak,
            "total_habits": habit_counts.get(email, 0),
        })

    results.sort(key=lambda x: x["best_streak"], reverse=True)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Admin helpers
# ─────────────────────────────────────────────────────────────────────────────


def admin_get_all_users(db_path):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT u.id, u.full_name, u.email, u.created_at,
                   ob.department, ob.overall_score,
                   fl.completed AS onboarding_done
            FROM users u
            LEFT JOIN onboarding_responses ob ON ob.email = u.email
            LEFT JOIN first_login fl ON fl.email = u.email
            ORDER BY u.created_at DESC
            """
        )
        return [dict(r) for r in cur.fetchall()]


def admin_get_user_details(db_path, email):
    """Return everything about a single user."""
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = dict(cur.fetchone()) if cur.fetchone() is None else None

    # re-fetch properly
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT id, full_name, email, created_at FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        user = dict(row) if row else None

    if not user:
        return None

    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM onboarding_responses WHERE email = ?", (email,))
        row = cur.fetchone()
        onboarding = dict(row) if row else None

        cur = conn.execute("SELECT data FROM skill_checklists WHERE email = ?", (email,))
        row = cur.fetchone()
        checklist = row["data"] if row else None

        cur = conn.execute(
            "SELECT * FROM mock_tests WHERE email = ? ORDER BY date_taken DESC", (email,)
        )
        mock_tests = [dict(r) for r in cur.fetchall()]

        cur = conn.execute(
            "SELECT id, filename, ats_score, created_at FROM resumes WHERE email = ? ORDER BY created_at DESC",
            (email,),
        )
        resumes = [dict(r) for r in cur.fetchall()]

        cur = conn.execute(
            "SELECT * FROM habits WHERE email = ? ORDER BY position", (email,)
        )
        habits = [dict(r) for r in cur.fetchall()]

        cur = conn.execute("SELECT * FROM first_login WHERE email = ?", (email,))
        row = cur.fetchone()
        first_login = dict(row) if row else None

    return {
        "user": user,
        "onboarding": onboarding,
        "checklist": checklist,
        "mock_tests": mock_tests,
        "resumes": resumes,
        "habits": habits,
        "first_login": first_login,
    }


def admin_get_stats(db_path):
    with get_connection(db_path) as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_resumes = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
        total_mock_tests = conn.execute("SELECT COUNT(*) FROM mock_tests").fetchone()[0]
        total_habits = conn.execute("SELECT COUNT(*) FROM habits").fetchone()[0]
        onboarded = conn.execute(
            "SELECT COUNT(*) FROM first_login WHERE completed = 1"
        ).fetchone()[0]

        # Avg ATS score
        cur = conn.execute("SELECT AVG(ats_score) FROM resumes WHERE ats_score IS NOT NULL")
        avg_ats = cur.fetchone()[0]

        # Avg onboarding score
        cur = conn.execute("SELECT AVG(overall_score) FROM onboarding_responses")
        avg_onboarding = cur.fetchone()[0]

        # Departments breakdown
        cur = conn.execute(
            "SELECT department, COUNT(*) as cnt FROM onboarding_responses GROUP BY department ORDER BY cnt DESC"
        )
        departments = [dict(r) for r in cur.fetchall()]

    return {
        "total_users": total_users,
        "total_resumes": total_resumes,
        "total_mock_tests": total_mock_tests,
        "total_habits": total_habits,
        "onboarded": onboarded,
        "avg_ats": round(avg_ats, 1) if avg_ats else 0,
        "avg_onboarding": round(avg_onboarding, 1) if avg_onboarding else 0,
        "departments": departments,
    }


def admin_delete_user(db_path, email):
    """Delete user and ALL related data."""
    with get_connection(db_path) as conn:
        # get habit ids for cascade
        cur = conn.execute("SELECT id FROM habits WHERE email = ?", (email,))
        habit_ids = [r["id"] for r in cur.fetchall()]
        for hid in habit_ids:
            conn.execute("DELETE FROM habit_logs WHERE habit_id = ?", (hid,))

        conn.execute("DELETE FROM habits WHERE email = ?", (email,))
        conn.execute("DELETE FROM mock_tests WHERE email = ?", (email,))
        conn.execute("DELETE FROM resumes WHERE email = ?", (email,))
        conn.execute("DELETE FROM skill_checklists WHERE email = ?", (email,))
        conn.execute("DELETE FROM onboarding_responses WHERE email = ?", (email,))
        conn.execute("DELETE FROM first_login WHERE email = ?", (email,))
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()


def admin_update_user(db_path, email, full_name=None, new_email=None):
    with get_connection(db_path) as conn:
        if full_name:
            conn.execute("UPDATE users SET full_name = ? WHERE email = ?", (full_name, email))
        if new_email and new_email != email:
            conn.execute("UPDATE users SET email = ? WHERE email = ?", (new_email, email))
            # update all related tables
            for table in ["first_login", "onboarding_responses", "skill_checklists",
                          "mock_tests", "resumes", "habits", "habit_logs"]:
                conn.execute(f"UPDATE {table} SET email = ? WHERE email = ?", (new_email, email))
        conn.commit()


def admin_run_query(db_path, query):
    """Run a raw SQL query (read-only SELECT for safety display, but allows all for admin)."""
    with get_connection(db_path) as conn:
        cur = conn.execute(query)
        if query.strip().upper().startswith("SELECT"):
            cols = [desc[0] for desc in cur.description] if cur.description else []
            rows = [dict(r) for r in cur.fetchall()]
            return {"columns": cols, "rows": rows, "affected": len(rows)}
        else:
            conn.commit()
            return {"columns": [], "rows": [], "affected": cur.rowcount}


def admin_get_table_names(db_path):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [r["name"] for r in cur.fetchall()]


def admin_get_table_data(db_path, table_name):
    """Get all rows from a specific table with column names."""
    # sanitize table name
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,))
        if not cur.fetchone():
            return None
        cur = conn.execute(f'SELECT * FROM "{table_name}" LIMIT 500')
        cols = [desc[0] for desc in cur.description] if cur.description else []
        rows = [dict(r) for r in cur.fetchall()]
        return {"columns": cols, "rows": rows}


def admin_delete_row(db_path, table_name, row_id):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,))
        if not cur.fetchone():
            return 0
        cur = conn.execute(f'DELETE FROM "{table_name}" WHERE id = ?', (row_id,))
        conn.commit()
        return cur.rowcount

def save_chat_message(db_path, email, user_message, assistant_response, context=""):
    """Save a chat message and response to chat history"""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO chat_history (email, user_message, assistant_response, context, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (email, user_message, assistant_response, context)
        )
        conn.commit()


def get_chat_history(db_path, email, limit=50):
    """Retrieve chat history for a user (most recent first)"""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT id, user_message, assistant_response, context, created_at
            FROM chat_history
            WHERE email = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (email, limit)
        )
        return [dict(row) for row in cur.fetchall()]


def get_chat_history_paginated(db_path, email, offset=0, limit=20):
    """Retrieve paginated chat history for a user"""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT id, user_message, assistant_response, context, created_at
            FROM chat_history
            WHERE email = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (email, limit, offset)
        )
        return [dict(row) for row in cur.fetchall()]


def delete_chat_history(db_path, email):
    """Delete all chat history for a user"""
    with get_connection(db_path) as conn:
        cur = conn.execute("DELETE FROM chat_history WHERE email = ?", (email,))
        conn.commit()
        return cur.rowcount


def delete_chat_message(db_path, message_id):
    """Delete a specific chat message"""
    with get_connection(db_path) as conn:
        cur = conn.execute("DELETE FROM chat_history WHERE id = ?", (message_id,))
        conn.commit()
        return cur.rowcount


# ─────────────────────────────────────────────────────────────────────────────
# Resources (Notes Platform)
# ─────────────────────────────────────────────────────────────────────────────

def create_resource(db_path, email, uploader_name, title, subject, branch,
                    year_of_engineering, academic_year, description, filename, file_path,
                    file_hash=None, file_size=None):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO resources
            (email, uploader_name, title, subject, branch, year_of_engineering,
             academic_year, description, filename, file_path, file_hash, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (email, uploader_name, title, subject, branch,
             year_of_engineering, academic_year, description, filename, file_path,
             file_hash, file_size),
        )
        conn.commit()
        return cur.lastrowid


def get_resource_by_hash(db_path, file_hash):
    if not file_hash:
        return None
    with get_connection(db_path) as conn:
        # Backfill hashes for legacy rows that were created before hash support.
        missing_rows = conn.execute(
            """
            SELECT id, file_path
            FROM resources
            WHERE status IN ('approved', 'pending')
              AND (file_hash IS NULL OR file_hash = '')
            """
        ).fetchall()

        for row in missing_rows:
            try:
                p = Path(row["file_path"])
                if not p.exists() or not p.is_file():
                    continue
                data = p.read_bytes()
                if not data:
                    continue
                computed_hash = hashlib.sha256(data).hexdigest()
                conn.execute(
                    "UPDATE resources SET file_hash = ?, file_size = ? WHERE id = ?",
                    (computed_hash, len(data), row["id"]),
                )
            except Exception:
                # Ignore unreadable files and keep processing others.
                continue

        conn.commit()

        cur = conn.execute(
            """
            SELECT * FROM resources
            WHERE file_hash = ? AND status IN ('approved', 'pending')
            ORDER BY uploaded_at DESC
            LIMIT 1
            """,
            (file_hash,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def list_approved_resources(db_path, branch=None, year=None, subject=None):
    with get_connection(db_path) as conn:
        query = "SELECT * FROM resources WHERE status = 'approved'"
        params = []
        if branch:
            query += " AND branch = ?"
            params.append(branch)
        if year:
            query += " AND year_of_engineering = ?"
            params.append(year)
        if subject:
            query += " AND subject LIKE ?"
            params.append(f"%{subject}%")
        query += " ORDER BY uploaded_at DESC"
        cur = conn.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def list_pending_resources(db_path):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM resources WHERE status = 'pending' ORDER BY uploaded_at DESC"
        )
        return [dict(r) for r in cur.fetchall()]


def list_pending_resources_paginated(db_path, page=1, page_size=3):
    page = max(1, int(page or 1))
    page_size = max(1, int(page_size or 3))
    offset = (page - 1) * page_size

    with get_connection(db_path) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM resources WHERE status = 'pending'"
        ).fetchone()[0]
        cur = conn.execute(
            """
            SELECT *
            FROM resources
            WHERE status = 'pending'
            ORDER BY uploaded_at DESC
            LIMIT ? OFFSET ?
            """,
            (page_size, offset),
        )
        items = [dict(r) for r in cur.fetchall()]

    total_pages = (total + page_size - 1) // page_size if total else 1
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
        },
    }


def list_approved_resources_paginated(db_path, page=1, page_size=5):
    page = max(1, int(page or 1))
    page_size = max(1, int(page_size or 5))
    offset = (page - 1) * page_size

    with get_connection(db_path) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM resources WHERE status = 'approved'"
        ).fetchone()[0]
        cur = conn.execute(
            """
            SELECT *
            FROM resources
            WHERE status = 'approved'
            ORDER BY reviewed_at DESC, uploaded_at DESC
            LIMIT ? OFFSET ?
            """,
            (page_size, offset),
        )
        items = [dict(r) for r in cur.fetchall()]

    total_pages = (total + page_size - 1) // page_size if total else 1
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
        },
    }


def list_user_resources(db_path, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM resources WHERE email = ? ORDER BY uploaded_at DESC",
            (email,),
        )
        return [dict(r) for r in cur.fetchall()]


def approve_resource(db_path, resource_id, admin_email):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE resources SET status = 'approved', reviewed_at = datetime('now'), reviewed_by = ? WHERE id = ?",
            (admin_email, resource_id),
        )
        conn.commit()


def reject_resource(db_path, resource_id, admin_email):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE resources SET status = 'rejected', reviewed_at = datetime('now'), reviewed_by = ? WHERE id = ?",
            (admin_email, resource_id),
        )
        conn.commit()


def get_resource_by_id(db_path, resource_id):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def delete_resource(db_path, resource_id, email):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM resources WHERE id = ? AND email = ?",
            (resource_id, email),
        )
        conn.commit()
        return cur.rowcount


def get_resource_stats(db_path):
    with get_connection(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]
        approved = conn.execute("SELECT COUNT(*) FROM resources WHERE status = 'approved'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM resources WHERE status = 'pending'").fetchone()[0]
        return {"total": total, "approved": approved, "pending": pending}


def update_resource(db_path, resource_id, email, title, subject, branch,
                    year_of_engineering, academic_year, description,
                    filename=None, file_path=None, file_hash=None, file_size=None):
    with get_connection(db_path) as conn:
        if filename and file_path:
            conn.execute(
                """UPDATE resources
                   SET title=?, subject=?, branch=?, year_of_engineering=?,
                       academic_year=?, description=?, filename=?, file_path=?,
                       file_hash=?, file_size=?,
                       status='pending', reviewed_at=NULL, reviewed_by=NULL
                   WHERE id=? AND email=?""",
                (title, subject, branch, year_of_engineering, academic_year,
                 description, filename, file_path, file_hash, file_size,
                 resource_id, email),
            )
        else:
            conn.execute(
                """UPDATE resources
                   SET title=?, subject=?, branch=?, year_of_engineering=?,
                       academic_year=?, description=?,
                       status='pending', reviewed_at=NULL, reviewed_by=NULL
                   WHERE id=? AND email=?""",
                (title, subject, branch, year_of_engineering, academic_year,
                 description, resource_id, email),
            )
        conn.commit()


def admin_update_resource_details(
    db_path,
    resource_id,
    title,
    subject,
    branch,
    year_of_engineering,
    academic_year,
    description,
):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE resources
            SET title=?, subject=?, branch=?, year_of_engineering=?,
                academic_year=?, description=?, reviewed_at=datetime('now')
            WHERE id=? AND status='approved'
            """,
            (
                title,
                subject,
                branch,
                year_of_engineering,
                academic_year,
                description,
                resource_id,
            ),
        )
        conn.commit()
        return cur.rowcount


def admin_delete_resource(db_path, resource_id):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM resources WHERE id = ? AND status = 'approved'",
            (resource_id,),
        )
        conn.commit()
        return cur.rowcount


def add_resource_comment(db_path, resource_id, commenter_email, commenter_name,
                         comment, is_admin=False):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO resource_comments
               (resource_id, commenter_email, commenter_name, comment, is_admin)
               VALUES (?, ?, ?, ?, ?)""",
            (resource_id, commenter_email, commenter_name, comment, 1 if is_admin else 0),
        )
        conn.commit()
        return cur.lastrowid


def get_resource_comments(db_path, resource_id):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM resource_comments WHERE resource_id = ? ORDER BY created_at ASC",
            (resource_id,),
        )
        return [dict(r) for r in cur.fetchall()]


# ─────────────────────────────────────────────────────────────────────────────
# AI Refinements
# ─────────────────────────────────────────────────────────────────────────────

def create_ai_refinement(db_path, resource_id, user_email):
    """Create a new AI refinement request."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO ai_refinements (resource_id, user_email, status)
               VALUES (?, ?, 'pending')""",
            (resource_id, user_email),
        )
        conn.commit()
        return cur.lastrowid


def get_ai_refinement(db_path, refinement_id):
    """Get AI refinement by ID."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM ai_refinements WHERE id = ?",
            (refinement_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_ai_refinement_by_resource(db_path, resource_id, user_email):
    """Get the latest AI refinement for a resource by a user."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """SELECT * FROM ai_refinements 
               WHERE resource_id = ? AND user_email = ?
               ORDER BY id DESC LIMIT 1""",
            (resource_id, user_email),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def update_ai_refinement(db_path, refinement_id, summary, questions_data, status='completed'):
    """Update AI refinement with results."""
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE ai_refinements 
               SET summary = ?, questions_data = ?, status = ?, 
                   completed_at = datetime('now')
               WHERE id = ?""",
            (summary, questions_data, status, refinement_id),
        )
        conn.commit()


def list_user_ai_refinements(db_path, user_email):
    """List all AI refinements for a user."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """SELECT ar.*, r.title as resource_title, r.subject as resource_subject
               FROM ai_refinements ar
               JOIN resources r ON ar.resource_id = r.id
               WHERE ar.user_email = ?
               ORDER BY ar.created_at DESC""",
            (user_email,),
        )
        return [dict(r) for r in cur.fetchall()]