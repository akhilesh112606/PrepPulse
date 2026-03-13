"""Simple migration script from sqlite file to Postgres DSN.

Usage:
    python scripts/migrate_sqlite_to_postgres.py --sqlite data/preppulse.db --postgres "postgresql://user:pw@host:5432/dbname"
"""
import argparse
import sqlite3

try:
    import psycopg2
    import psycopg2.extras
except Exception as e:
    psycopg2 = None

TABLES = [
    "users",
    "first_login",
    "onboarding_responses",
    "skill_checklists",
    "mock_tests",
    "resumes",
    "habits",
    "habit_logs",
]

INSERT_SQL = {
    "users": (
        "id, full_name, email, password_hash, created_at",
        "VALUES (%s, %s, %s, %s, %s)",
    ),
    "first_login": (
        "id, email, completed, created_at, updated_at",
        "VALUES (%s, %s, %s, %s, %s)",
    ),
    "onboarding_responses": (
        "id, email, department, problem_solving, resume_ready, interview_ready, consistency, overall_score, created_at",
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
    ),
    "skill_checklists": (
        "id, email, data, created_at, updated_at",
        "VALUES (%s, %s, %s, %s, %s)",
    ),
    "mock_tests": (
        "id, email, test_name, source, score, max_score, date_taken, notes, created_at, updated_at",
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    ),
    "resumes": (
        "id, email, filename, file_path, file_content, analysis_data, ats_score, created_at, updated_at",
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
    ),
    "habits": (
        "id, email, name, color, position, created_at",
        "VALUES (%s, %s, %s, %s, %s, %s)",
    ),
    "habit_logs": (
        "id, habit_id, email, log_date, done",
        "VALUES (%s, %s, %s, %s, %s)",
    ),
}

SEQUENCE_FIX_SQL = {
    "users": "SELECT setval(pg_get_serial_sequence('users','id'), COALESCE((SELECT max(id)+1 FROM users),1), false);",
    "first_login": "SELECT setval(pg_get_serial_sequence('first_login','id'), COALESCE((SELECT max(id)+1 FROM first_login),1), false);",
    "onboarding_responses": "SELECT setval(pg_get_serial_sequence('onboarding_responses','id'), COALESCE((SELECT max(id)+1 FROM onboarding_responses),1), false);",
    "skill_checklists": "SELECT setval(pg_get_serial_sequence('skill_checklists','id'), COALESCE((SELECT max(id)+1 FROM skill_checklists),1), false);",
    "mock_tests": "SELECT setval(pg_get_serial_sequence('mock_tests','id'), COALESCE((SELECT max(id)+1 FROM mock_tests),1), false);",
    "resumes": "SELECT setval(pg_get_serial_sequence('resumes','id'), COALESCE((SELECT max(id)+1 FROM resumes),1), false);",
    "habits": "SELECT setval(pg_get_serial_sequence('habits','id'), COALESCE((SELECT max(id)+1 FROM habits),1), false);",
    "habit_logs": "SELECT setval(pg_get_serial_sequence('habit_logs','id'), COALESCE((SELECT max(id)+1 FROM habit_logs),1), false);",
}


def migrate(sqlite_path, pg_dsn):
    if not psycopg2:
        raise RuntimeError("psycopg2 is required to run this migration script. Install psycopg2-binary.")

    sconn = sqlite3.connect(sqlite_path)
    sconn.row_factory = sqlite3.Row
    scur = sconn.cursor()

    pconn = psycopg2.connect(pg_dsn)
    pcur = pconn.cursor()

    try:
        # create tables in Postgres if they don't exist
        from app.db import init_db as app_init_db

        # reuse the app db initializer via a quick wrapper app-like dict
        class DummyApp:
            def __init__(self, dsn):
                self.config = {"DATABASE": dsn}

        app_init_db(DummyApp(pg_dsn))

        # truncate target tables
        for t in TABLES:
            pcur.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;")
        pconn.commit()

        # copy rows
        for t in TABLES:
            scur.execute(f"SELECT * FROM {t}")
            rows = scur.fetchall()
            if not rows:
                continue
            cols, vals_tpl = INSERT_SQL[t]
            insert_sql = f"INSERT INTO {t} ({cols}) {vals_tpl}"
            if t == "onboarding_responses":
                # avoid conflict on unique email - simple insert is fine after truncation
                pass

            for r in rows:
                vals = [r[c] if c in r.keys() else None for c in cols.replace(' ', '').split(',')]
                # Normalize sqlite returns: convert bytes to str
                vals = [v.decode('utf-8') if isinstance(v, (bytes, bytearray)) else v for v in vals]
                pcur.execute(insert_sql, vals)
            pconn.commit()

        # fix sequences
        for t, seq_sql in SEQUENCE_FIX_SQL.items():
            pcur.execute(seq_sql)
        pconn.commit()

        print("Migration completed successfully.")
    finally:
        scur.close()
        sconn.close()
        pcur.close()
        pconn.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sqlite", required=True, help="Path to sqlite file")
    p.add_argument("--postgres", required=True, help="Postgres DSN e.g. postgresql://user:pw@host:5432/db")
    args = p.parse_args()

    migrate(args.sqlite, args.postgres)


if __name__ == "__main__":
    main()
