
import sqlite3
from datetime import datetime

DB_NAME = "database/outreach.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn.commit()
    conn.close()

def save_email(name, role, company, industry, tone, email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO outreach (name, role, company, industry, tone, email, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, role, company, industry, tone, email, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, role, company, industry, tone, created_at FROM outreach ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows
