import sqlite3
from pathlib import Path


def init_db(app):
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
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS first_login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
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
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS skill_checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
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
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
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
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
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
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
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
        conn.commit()


def get_connection(db_path):
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
