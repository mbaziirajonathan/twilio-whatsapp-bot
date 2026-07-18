# database.py
import sqlite3
import json
from datetime import datetime
import pytz

DB_NAME = "sessions.db"
UGANDA_TZ = pytz.timezone("Africa/Kampala")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (user_id TEXT, subject TEXT, class_level TEXT,
                  chat_history TEXT, activities_log TEXT,
                  PRIMARY KEY(user_id, subject, class_level))''')
    conn.commit()
    conn.close()

def get_session(user_id: str, subject: str, class_level: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT chat_history, activities_log FROM sessions WHERE user_id=? AND subject=? AND class_level=?",
              (user_id, subject, class_level))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]), json.loads(row[1])
    else:
        return [], [] # New user

def save_session(user_id: str, subject: str, class_level: str, chat_history: list, activities_log: list):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO sessions (user_id, subject, class_level, chat_history, activities_log) VALUES (?,?,?,?,?)",
              (user_id, subject, class_level, json.dumps(chat_history), json.dumps(activities_log)))
    conn.commit()
    conn.close()

def log_activity(user_id, subject, class_level, activity):
    chat, log = get_session(user_id, subject, class_level)
    log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity})
    save_session(user_id, subject, class_level, chat, log)

init_db()
