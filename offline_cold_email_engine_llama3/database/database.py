import sqlite3
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
                created_at TEXT
            )
        ''')
        # Migration check
        try:
            c.execute("SELECT persona_summary FROM outreach LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE outreach ADD COLUMN persona_summary TEXT")
        conn.commit()

def save_email(name, role, company, industry, tone, email, persona_summary):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO outreach (name, role, company, industry, tone, email, persona_summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, role, company, industry, tone, email, persona_summary, datetime.now().isoformat()))
        conn.commit()

def get_all_records():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT name, role, company, industry, tone, created_at, 
            COALESCE(persona_summary, 'Legacy Record') as persona_summary, email 
            FROM outreach ORDER BY id DESC
        """)
        return c.fetchall()