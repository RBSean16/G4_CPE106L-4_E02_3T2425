from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sqlite3
import os

app = FastAPI()

# Static directory setup
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ──────── DATABASE INITIALIZATION ────────

def init_db():
    with sqlite3.connect("wellness.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL)''')
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

init_db()

# ──────── Pydantic MODELS ────────

class UserInput(BaseModel):
    user_id: int
    name: str

class MoodInput(BaseModel):
    user_id: int
    mood_score: int
    notes: str = ""

class JournalInput(BaseModel):
    user_id: int
    content: str

class Recommendation(BaseModel):
    strategy: str
    reason: str

# ──────── API ROUTES ────────

@app.post("/api/create-user")
def create_user(user: UserInput):
    with sqlite3.connect("wellness.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user.user_id,))
        existing_user = c.fetchone()
        if existing_user:
            return {"message": "User already exists"}
        c.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user.user_id, user.name))
        conn.commit()
    return {"message": "User created"}

@app.post("/api/mood-entry")
def add_mood(entry: MoodInput):
    with sqlite3.connect("wellness.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO mood_entries (user_id, mood_score, notes, date) VALUES (?, ?, ?, ?)",
                  (entry.user_id, entry.mood_score, entry.notes, date.today().isoformat()))
        conn.commit()
    return {"message": "Mood entry added"}

@app.post("/api/journal-entry")
def add_journal(entry: JournalInput):
    with sqlite3.connect("wellness.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO journal_entries (user_id, content, date) VALUES (?, ?, ?)",
                  (entry.user_id, entry.content, date.today().isoformat()))
        conn.commit()
    return {"message": "Journal entry added"}

@app.get("/api/recommendation/{user_id}")
def get_recommendation(user_id: int):
    with sqlite3.connect("wellness.db") as conn:
        c = conn.cursor()
        c.execute("SELECT mood_score FROM mood_entries WHERE user_id = ?", (user_id,))
        moods = [row[0] for row in c.fetchall()]

    if not moods:
        raise HTTPException(status_code=404, detail="No mood data found for the user")

    avg = sum(moods) / len(moods)
    if avg < 4:
        return {"strategy": "Practice Gratitude", "reason": "Your mood scores suggest you may be feeling down. Gratitude exercises can help improve your outlook."}
    elif avg > 7:
        return {"strategy": "Maintain Positive Habits", "reason": "Your mood scores suggest you're doing well. Keep up the good work!"}
    else:
        return {"strategy": "Mindfulness Meditation", "reason": "Your mood scores suggest a neutral state. Mindfulness can help bring clarity and balance."}

# ──────── CHART GENERATION ────────

@app.get("/api/mood-trend/{user_id}")
def mood_trend(user_id: int):
    with sqlite3.connect("wellness.db") as conn:
        df = pd.read_sql_query(
            "SELECT date, mood_score FROM mood_entries WHERE user_id = ? ORDER BY date ASC", conn, params=(user_id,))
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No mood data found")

    df['date'] = pd.to_datetime(df['date'])
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['mood_score'], marker='o', linestyle='-', color='blue')
    plt.title("Mood Trend")
    plt.xlabel("Date")
    plt.ylabel("Mood Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"static/mood_trend_{user_id}.png"
    plt.savefig(path)
    plt.close()
    return FileResponse(path, media_type="image/png")

@app.get("/api/journal-heatmap/{user_id}")
def journal_heatmap(user_id: int):
    with sqlite3.connect("wellness.db") as conn:
        df = pd.read_sql_query(
            "SELECT date FROM journal_entries WHERE user_id = ?", conn, params=(user_id,))
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No journal data found")

    df['date'] = pd.to_datetime(df['date'])
    df['weekday'] = df['date'].dt.day_name()
    df['day'] = df['date'].dt.day
    heatmap_data = df.groupby(['weekday', 'day']).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap='YlGnBu', linewidths=0.5, linecolor='gray')
    plt.title("Journaling Heatmap")
    plt.xlabel("Day")
    plt.ylabel("Weekday")
    plt.tight_layout()
    path = f"static/journal_heatmap_{user_id}.png"
    plt.savefig(path)
    plt.close()
    return FileResponse(path, media_type="image/png")

@app.get("/api/wellness-scores")
def wellness_scores_chart():
    scores = {
        'Sleep': 7,
        'Exercise': 5,
        'Mindfulness': 6,
        'Nutrition': 8,
        'Social': 4
    }
    df = pd.DataFrame({'Category': list(scores.keys()), 'Score': list(scores.values())})
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='Category', y='Score', hue='Category', palette='viridis', legend=False)
    plt.title("Wellness Score Comparison")
    plt.ylabel("Score")
    plt.ylim(0, 10)
    plt.tight_layout()
    path = "static/wellness_scores.png"
    plt.savefig(path)
    plt.close()
    return FileResponse(path, media_type="image/png")
