# back.py

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from typing import List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sqlite3
import os
import hashlib
import numpy as np

# --- FastAPI App Initialization ---
app = FastAPI(title="Community Mental Health Tracker", version="1.0.0")

# --- Static Directory Setup ---
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- DATA LAYER (DatabaseManager) ---
class DatabaseManager:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect("wellness.db")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def init_db():
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                           user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL UNIQUE,
                           password_hash TEXT NOT NULL,
                           created_at TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS mood_entries (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           mood_score INTEGER,
                           notes TEXT,
                           date TEXT,
                           FOREIGN KEY(user_id) REFERENCES users(user_id))''')
            c.execute('''CREATE TABLE IF NOT EXISTS journal_entries (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           content TEXT,
                           date TEXT,
                           FOREIGN KEY(user_id) REFERENCES users(user_id))''')
            conn.commit()

    @staticmethod
    def get_user_by_name(name: str):
        with DatabaseManager.get_connection() as conn:
            return conn.cursor().execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()

    @staticmethod
    def create_user(name: str, password: str) -> Optional[dict]:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        created_at = datetime.now().isoformat()
        with DatabaseManager.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, password_hash, created_at) VALUES (?, ?, ?)",
                               (name, password_hash, created_at))
                conn.commit()
                return {"user_id": cursor.lastrowid, "name": name}
            except sqlite3.IntegrityError:
                return None # User already exists
    
    @staticmethod
    def add_mood_entry(user_id: int, mood_score: int, notes: str):
        with DatabaseManager.get_connection() as conn:
            conn.execute("INSERT INTO mood_entries (user_id, mood_score, notes, date) VALUES (?, ?, ?, ?)",
                         (user_id, mood_score, notes, datetime.now().date().isoformat()))
            conn.commit()

    @staticmethod
    def add_journal_entry(user_id: int, content: str):
        with DatabaseManager.get_connection() as conn:
            conn.execute("INSERT INTO journal_entries (user_id, content, date) VALUES (?, ?, ?)",
                         (user_id, content, datetime.now().date().isoformat()))
            conn.commit()

    @staticmethod
    def get_journal_entries(user_id: int):
        with DatabaseManager.get_connection() as conn:
            return conn.cursor().execute("SELECT date FROM journal_entries WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()

    @staticmethod
    def get_mood_entries(user_id: int, limit: int = 30):
        with DatabaseManager.get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM mood_entries WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit)).fetchall()
            return [dict(row) for row in rows]


DatabaseManager.init_db()

# --- Pydantic Models for API input ---
class UserAuthInput(BaseModel):
    name: str
    password: str

# FIX: Restored the missing Pydantic models
class MoodInput(BaseModel):
    user_id: int
    mood_score: int
    notes: Optional[str] = ""

class JournalInput(BaseModel):
    user_id: int
    content: str

# --- API ROUTES ---
@app.post("/api/register", tags=["Authentication"])
def register_user(user_input: UserAuthInput):
    new_user = DatabaseManager.create_user(user_input.name, user_input.password)
    if new_user:
        return {"message": "User created successfully", "user": new_user}
    raise HTTPException(status_code=409, detail="An account with this username already exists.")

@app.post("/api/login", tags=["Authentication"])
def login_user(user_input: UserAuthInput):
    print("--- LOGIN ENDPOINT CALLED WITH NEW CODE ---")
    user = DatabaseManager.get_user_by_name(user_input.name)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with that username.")
    
    password_hash = hashlib.sha256(user_input.password.encode()).hexdigest()
    if password_hash == user['password_hash']:
        return {"message": "Login successful", "user_id": user['user_id'], "name": user['name']}
    raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
    
@app.post("/api/mood-entry", tags=["Mood Tracking"])
def add_mood(entry: MoodInput):
    DatabaseManager.add_mood_entry(entry.user_id, entry.mood_score, entry.notes)
    return {"message": "Mood entry added successfully"}

@app.post("/api/journal-entry", tags=["Journaling"])
def add_journal(entry: JournalInput):
    DatabaseManager.add_journal_entry(entry.user_id, entry.content)
    return {"message": "Journal entry added successfully"}

@app.get("/api/journal-dates/{user_id}", tags=["Journaling"])
def get_journal_dates(user_id: int):
    entries = DatabaseManager.get_journal_entries(user_id)
    return {"dates": [entry['date'] for entry in entries]}