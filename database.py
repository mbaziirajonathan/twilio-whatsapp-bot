import sqlite3
import os
from datetime import datetime

DB_NAME = "chat_history.db"

def init_db():
    """Run this once on startup"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  phone_number TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(phone_number, role, content):
    """role = 'user' or 'assistant'"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (phone_number, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (phone_number, role, content, datetime.now()))
    conn.commit()
    conn.close()

def get_chat_history(phone_number, limit=6):
    """Get last 6 messages = 3 exchanges. Matches ai_logic.py"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE phone_number = ? ORDER BY id DESC LIMIT ?",
              (phone_number, limit))
    rows = c.fetchall()
    conn.close()
    
    # Reverse to get chronological order for Groq
    history = [(role, content) for role, content in reversed(rows)]
    return history

def clear_history(phone_number):
    """For 'reset' command"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE phone_number = ?", (phone_number,))
    conn.commit()
    conn.close()
