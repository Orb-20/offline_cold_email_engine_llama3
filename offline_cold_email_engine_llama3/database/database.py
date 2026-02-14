import sqlite3
import json
from datetime import datetime

DB_NAME = "database/outreach.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                company TEXT,
                industry TEXT,
                tone TEXT,
                email TEXT,
                created_at TEXT,
                persona_summary TEXT
            )
        ''')
        # Migration for new features if needed
        try:
            c.execute("ALTER TABLE outreach ADD COLUMN persona_summary TEXT")
        except: pass
        conn.commit()

def save_email(*args):
    """
    Flexible save function to handle varying argument counts 
    from different versions of the app.
    Arguments expected order: name, role, company, industry, tone, email, [persona_summary]
    """
    # Unpack based on length
    name = args[0] if len(args) > 0 else "Unknown"
    role = args[1] if len(args) > 1 else "Unknown"
    company = args[2] if len(args) > 2 else "Unknown"
    industry = args[3] if len(args) > 3 else "Unknown"
    tone = args[4] if len(args) > 4 else "Unknown"
    email = args[5] if len(args) > 5 else ""
    summary = args[6] if len(args) > 6 else "Auto-Generated"

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO outreach (name, role, company, industry, tone, email, persona_summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, role, company, industry, tone, email, summary, datetime.now().isoformat()))
        conn.commit()

def get_all_records():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM outreach ORDER BY id DESC")
        return [dict(row) for row in c.fetchall()]