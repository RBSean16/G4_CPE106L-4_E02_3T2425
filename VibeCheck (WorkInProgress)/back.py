from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from typing import List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sqlite3
import os
import hashlib
import jwt
from collections import defaultdict
import numpy as np

app = FastAPI(title="Community Mental Health Tracker", version="1.0.0")
security = HTTPBearer()

# Static directory setup
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# JWT Secret (in production, use environment variable)
JWT_SECRET = "your-secret-key-here"

# ──────── OOP CLASSES (Object Oriented Design) ────────

class User:
    def __init__(self, user_id: int, name: str, email: str = "", created_at: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at
        }

class MoodEntry:
    def __init__(self, entry_id: int, user_id: int, mood_score: int, notes: str = "", date: str = None):
        self.entry_id = entry_id
        self.user_id = user_id
        self.mood_score = mood_score
        self.notes = notes
        self.date = date or datetime.now().date().isoformat()
    
    def to_dict(self):
        return {
            "id": self.entry_id,
            "user_id": self.user_id,
            "mood_score": self.mood_score,
            "notes": self.notes,
            "date": self.date
        }

class JournalEntry:
    def __init__(self, entry_id: int, user_id: int, content: str, date: str = None):
        self.entry_id = entry_id
        self.user_id = user_id
        self.content = content
        self.date = date or datetime.now().date().isoformat()
    
    def to_dict(self):
        return {
            "id": self.entry_id,
            "user_id": self.user_id,
            "content": self.content,
            "date": self.date
        }

class RecommendationEngine:
    """Optimization Algorithm for suggesting coping strategies"""
    
    @staticmethod
    def analyze_mood_patterns(mood_entries: List[MoodEntry]) -> dict:
        """Analyze mood patterns using optimization algorithms"""
        if not mood_entries:
            return {"avg_mood": 0, "trend": "stable", "volatility": 0}
        
        scores = [entry.mood_score for entry in mood_entries]
        avg_mood = np.mean(scores)
        
        # Calculate trend using linear regression
        if len(scores) > 1:
            x = np.arange(len(scores))
            trend_coef = np.polyfit(x, scores, 1)[0]
            trend = "improving" if trend_coef > 0.1 else "declining" if trend_coef < -0.1 else "stable"
        else:
            trend = "stable"
        
        # Calculate volatility (standard deviation)
        volatility = np.std(scores) if len(scores) > 1 else 0
        
        return {
            "avg_mood": avg_mood,
            "trend": trend,
            "volatility": volatility,
            "recent_scores": scores[-7:] if len(scores) > 7 else scores
        }
    
    @staticmethod
    def get_optimal_recommendation(mood_analysis: dict) -> dict:
        """Get optimal coping strategy based on mood patterns"""
        avg_mood = mood_analysis["avg_mood"]
        trend = mood_analysis["trend"]
        volatility = mood_analysis["volatility"]
        
        # Optimization: Select best strategy based on multiple factors
        if avg_mood < 3:
            if trend == "declining":
                return {
                    "strategy": "Crisis Support & Professional Help",
                    "reason": "Your mood has been consistently low and declining. Consider reaching out to a mental health professional.",
                    "priority": "high",
                    "actions": ["Contact a therapist", "Use crisis hotline", "Reach out to trusted friends"]
                }
            else:
                return {
                    "strategy": "Cognitive Behavioral Techniques",
                    "reason": "Your mood scores suggest you're going through a difficult time. CBT techniques can help reframe negative thoughts.",
                    "priority": "high",
                    "actions": ["Practice thought challenging", "Keep a mood diary", "Try deep breathing exercises"]
                }
        elif avg_mood < 5:
            if volatility > 2:
                return {
                    "strategy": "Emotional Regulation & Stability",
                    "reason": "Your mood shows high volatility. Focus on building emotional stability through routine.",
                    "priority": "medium",
                    "actions": ["Establish daily routine", "Practice mindfulness", "Regular sleep schedule"]
                }
            else:
                return {
                    "strategy": "Gradual Mood Improvement",
                    "reason": "Your mood is neutral but could benefit from positive activities.",
                    "priority": "medium",
                    "actions": ["Engage in pleasant activities", "Exercise regularly", "Connect with friends"]
                }
        elif avg_mood < 7:
            return {
                "strategy": "Mindfulness & Self-Care",
                "reason": "Your mood is generally positive. Mindfulness can help maintain this state.",
                "priority": "low",
                "actions": ["Daily meditation", "Gratitude journaling", "Regular self-care activities"]
            }
        else:
            if trend == "improving":
                return {
                    "strategy": "Maintain Positive Momentum",
                    "reason": "Your mood is excellent and improving! Keep up the great work.",
                    "priority": "low",
                    "actions": ["Continue current habits", "Share positivity with others", "Set new goals"]
                }
            else:
                return {
                    "strategy": "Sustain Well-being",
                    "reason": "Your mood is great! Focus on maintaining these positive patterns.",
                    "priority": "low",
                    "actions": ["Maintain healthy routines", "Practice gratitude", "Help others"]
                }

# ──────── DATA LAYER (Model in MVC) ────────

class DatabaseManager:
    """Data access layer for managing database operations"""
    
    @staticmethod
    def get_connection():
        return sqlite3.connect("wellness.db")
    
    @staticmethod
    def init_db():
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            # Enhanced user table
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            email TEXT,
                            password_hash TEXT,
                            created_at TEXT)''')
            
            # Enhanced mood entries table
            c.execute('''CREATE TABLE IF NOT EXISTS mood_entries (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            mood_score INTEGER,
                            notes TEXT,
                            date TEXT,
                            created_at TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(user_id))''')
            
            # Enhanced journal entries table
            c.execute('''CREATE TABLE IF NOT EXISTS journal_entries (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            content TEXT,
                            date TEXT,
                            created_at TEXT,
                            word_count INTEGER,
                            FOREIGN KEY(user_id) REFERENCES users(user_id))''')
            
            # New table for tracking user sessions
            c.execute('''CREATE TABLE IF NOT EXISTS user_sessions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            session_token TEXT,
                            created_at TEXT,
                            expires_at TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(user_id))''')
            
            conn.commit()
    
    @staticmethod
    def create_user(user: User, password: str = None) -> bool:
        try:
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE user_id = ?", (user.user_id,))
                if c.fetchone():
                    return False
                
                password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
                c.execute("INSERT INTO users (user_id, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                         (user.user_id, user.name, user.email, password_hash, user.created_at))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        try:
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT user_id, name, email, created_at FROM users WHERE user_id = ?", (user_id,))
                row = c.fetchone()
                if row:
                    return User(row[0], row[1], row[2], row[3])
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def add_mood_entry(entry: MoodEntry) -> bool:
        try:
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                c.execute("INSERT INTO mood_entries (user_id, mood_score, notes, date, created_at) VALUES (?, ?, ?, ?, ?)",
                         (entry.user_id, entry.mood_score, entry.notes, entry.date, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding mood entry: {e}")
            return False
    
    @staticmethod
    def get_mood_entries(user_id: int, limit: int = None) -> List[MoodEntry]:
        try:
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                query = "SELECT id, user_id, mood_score, notes, date FROM mood_entries WHERE user_id = ? ORDER BY date DESC"
                if limit:
                    query += f" LIMIT {limit}"
                c.execute(query, (user_id,))
                entries = []
                for row in c.fetchall():
                    entries.append(MoodEntry(row[0], row[1], row[2], row[3], row[4]))
                return entries
        except Exception as e:
            print(f"Error getting mood entries: {e}")
            return []
    
    @staticmethod
    def add_journal_entry(entry: JournalEntry) -> bool:
        try:
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                word_count = len(entry.content.split())
                c.execute("INSERT INTO journal_entries (user_id, content, date, created_at, word_count) VALUES (?, ?, ?, ?, ?)",
                         (entry.user_id, entry.content, entry.date, datetime.now().isoformat(), word_count))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding journal entry: {e}")
            return False
    
    @staticmethod
    def get_journal_entries(user_id: int, limit: int = None) -> List[JournalEntry]:
        try:
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                query = "SELECT id, user_id, content, date FROM journal_entries WHERE user_id = ? ORDER BY date DESC"
                if limit:
                    query += f" LIMIT {limit}"
                c.execute(query, (user_id,))
                entries = []
                for row in c.fetchall():
                    entries.append(JournalEntry(row[0], row[1], row[2], row[3]))
                return entries
        except Exception as e:
            print(f"Error getting journal entries: {e}")
            return []

# Initialize database
DatabaseManager.init_db()

# ──────── BUSINESS LOGIC LAYER (Controller in MVC) ────────

class MentalHealthController:
    """Business logic layer for mental health operations"""
    
    @staticmethod
    def process_mood_entry(user_id: int, mood_score: int, notes: str) -> dict:
        """Process and validate mood entry"""
        if not (1 <= mood_score <= 10):
            raise HTTPException(status_code=400, detail="Mood score must be between 1 and 10")
        
        entry = MoodEntry(0, user_id, mood_score, notes)
        success = DatabaseManager.add_mood_entry(entry)
        
        if success:
            return {"message": "Mood entry added successfully", "entry": entry.to_dict()}
        else:
            raise HTTPException(status_code=500, detail="Failed to save mood entry")
    
    @staticmethod
    def process_journal_entry(user_id: int, content: str) -> dict:
        """Process and validate journal entry"""
        if not content.strip():
            raise HTTPException(status_code=400, detail="Journal content cannot be empty")
        
        entry = JournalEntry(0, user_id, content.strip())
        success = DatabaseManager.add_journal_entry(entry)
        
        if success:
            return {"message": "Journal entry added successfully", "entry": entry.to_dict()}
        else:
            raise HTTPException(status_code=500, detail="Failed to save journal entry")
    
    @staticmethod
    def generate_recommendations(user_id: int) -> dict:
        """Generate personalized recommendations using optimization algorithms"""
        mood_entries = DatabaseManager.get_mood_entries(user_id, limit=30)  # Last 30 entries
        
        if not mood_entries:
            raise HTTPException(status_code=404, detail="No mood data found for recommendations")
        
        # Analyze patterns
        mood_analysis = RecommendationEngine.analyze_mood_patterns(mood_entries)
        
        # Get optimal recommendation
        recommendation = RecommendationEngine.get_optimal_recommendation(mood_analysis)
        
        return {
            "recommendation": recommendation,
            "analysis": mood_analysis,
            "data_points": len(mood_entries)
        }

# ──────── Pydantic MODELS (Data Transfer Objects) ────────

class UserInput(BaseModel):
    user_id: int
    name: str
    email: Optional[str] = ""
    password: Optional[str] = ""

class MoodInput(BaseModel):
    user_id: int
    mood_score: int
    notes: str = ""

class JournalInput(BaseModel):
    user_id: int
    content: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    created_at: str

class MoodResponse(BaseModel):
    id: int
    user_id: int
    mood_score: int
    notes: str
    date: str

class JournalResponse(BaseModel):
    id: int
    user_id: int
    content: str
    date: str

# ──────── API ROUTES (View Layer in MVC) ────────

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "healthy", "app": "Community Mental Health Tracker", "version": "1.0.0"}

@app.post("/api/login", tags=["Authentication"])
def login(user_input: UserInput):
    """Authenticate a user"""
    if not user_input.password:
        raise HTTPException(status_code=400, detail="Password required")
    
    user = DatabaseManager.get_user(user_input.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password (simplified for example)
    password_hash = hashlib.sha256(user_input.password.encode()).hexdigest()
    stored_hash = password_hash(user_input.user_id)  # You'll need to implement this
    
    if password_hash != stored_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "user": user.to_dict()}

@app.post("/api/create-user", response_model=dict, tags=["User Management"])
def create_user(user_input: UserInput):
    """Create a new user in the system"""
    if not user_input.password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    user = User(user_input.user_id, user_input.name, user_input.email)
    success = DatabaseManager.create_user(user, user_input.password)
    
    if success:
        return {"message": "User created successfully", "user": user.to_dict()}
    else:
        return {"message": "User already exists", "user_id": user_input.user_id}

@app.get("/api/user/{user_id}", response_model=UserResponse, tags=["User Management"])
def get_user(user_id: int):
    """Get user information"""
    user = DatabaseManager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()

@app.post("/api/mood-entry", tags=["Mood Tracking"])
def add_mood(entry: MoodInput):
    """Add a new mood entry"""
    return MentalHealthController.process_mood_entry(entry.user_id, entry.mood_score, entry.notes)

@app.get("/api/mood-entries/{user_id}", response_model=List[MoodResponse], tags=["Mood Tracking"])
def get_mood_entries(user_id: int, limit: int = 30):
    """Get user's mood entries"""
    entries = DatabaseManager.get_mood_entries(user_id, limit)
    return [entry.to_dict() for entry in entries]

@app.post("/api/journal-entry", tags=["Journaling"])
def add_journal(entry: JournalInput):
    """Add a new journal entry"""
    return MentalHealthController.process_journal_entry(entry.user_id, entry.content)

@app.get("/api/journal-entries/{user_id}", response_model=List[JournalResponse], tags=["Journaling"])
def get_journal_entries(user_id: int, limit: int = 10):
    """Get user's journal entries"""
    entries = DatabaseManager.get_journal_entries(user_id, limit)
    return [entry.to_dict() for entry in entries]

@app.get("/api/recommendation/{user_id}", tags=["AI Recommendations"])
def get_recommendation(user_id: int):
    """Get personalized recommendations based on mood patterns"""
    return MentalHealthController.generate_recommendations(user_id)

@app.get("/api/analytics/{user_id}", tags=["Analytics"])
def get_user_analytics(user_id: int):
    """Get comprehensive user analytics"""
    mood_entries = DatabaseManager.get_mood_entries(user_id)
    journal_entries = DatabaseManager.get_journal_entries(user_id)
    
    if not mood_entries and not journal_entries:
        raise HTTPException(status_code=404, detail="No data found for user")
    
    mood_analysis = RecommendationEngine.analyze_mood_patterns(mood_entries) if mood_entries else {}
    
    return {
        "user_id": user_id,
        "mood_entries_count": len(mood_entries),
        "journal_entries_count": len(journal_entries),
        "mood_analysis": mood_analysis,
        "activity_streak": calculate_activity_streak(user_id),
        "last_active": get_last_activity_date(user_id)
    }

def calculate_activity_streak(user_id: int) -> int:
    """Calculate consecutive days of activity"""
    with DatabaseManager.get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT date FROM (
                SELECT date FROM mood_entries WHERE user_id = ?
                UNION
                SELECT date FROM journal_entries WHERE user_id = ?
            ) ORDER BY date DESC
        """, (user_id, user_id))
        
        dates = [row[0] for row in c.fetchall()]
        if not dates:
            return 0
        
        streak = 1
        current_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
        
        for date_str in dates[1:]:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if (current_date - date_obj).days == 1:
                streak += 1
                current_date = date_obj
            else:
                break
        
        return streak

def get_last_activity_date(user_id: int) -> str:
    """Get the last activity date for a user"""
    with DatabaseManager.get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT MAX(date) FROM (
                SELECT date FROM mood_entries WHERE user_id = ?
                UNION
                SELECT date FROM journal_entries WHERE user_id = ?
            )
        """, (user_id, user_id))
        
        result = c.fetchone()
        return result[0] if result and result[0] else "Never"

# ──────── ENHANCED CHART GENERATION (Matplotlib Integration) ────────

@app.get("/api/mood-trend/{user_id}", tags=["Visualizations"])
def mood_trend(user_id: int):
    """Generate mood trend chart with enhanced analytics"""
    mood_entries = DatabaseManager.get_mood_entries(user_id)
    
    if not mood_entries:
        raise HTTPException(status_code=404, detail="No mood data found")

    # Create DataFrame
    data = [(entry.date, entry.mood_score) for entry in mood_entries]
    df = pd.DataFrame(data, columns=['date', 'mood_score'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Enhanced visualization
    plt.figure(figsize=(12, 8))
    
    # Main plot
    plt.subplot(2, 1, 1)
    plt.plot(df['date'], df['mood_score'], marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.title(f"Mood Trend Analysis - User {user_id}", fontsize=16, fontweight='bold')
    plt.xlabel("Date")
    plt.ylabel("Mood Score")
    plt.grid(True, alpha=0.3)
    
    # Add trend line
    if len(df) > 1:
        z = np.polyfit(range(len(df)), df['mood_score'], 1)
        p = np.poly1d(z)
        plt.plot(df['date'], p(range(len(df))), "--", alpha=0.7, color='red', label=f"Trend: {'↗' if z[0] > 0 else '↘'}")
        plt.legend()
    
    # Statistics subplot
    plt.subplot(2, 1, 2)
    weekly_avg = df.set_index('date').resample('W')['mood_score'].mean()
    plt.bar(weekly_avg.index, weekly_avg.values, alpha=0.7, color='skyblue')
    plt.title("Weekly Average Mood", fontsize=14)
    plt.xlabel("Week")
    plt.ylabel("Average Mood Score")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    path = f"static/mood_trend_{user_id}.png"
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return FileResponse(path, media_type="image/png")

@app.get("/api/journal-heatmap/{user_id}", tags=["Visualizations"])
def journal_heatmap(user_id: int):
    """Generate enhanced journal activity heatmap"""
    journal_entries = DatabaseManager.get_journal_entries(user_id)
    
    if not journal_entries:
        raise HTTPException(status_code=404, detail="No journal data found")

    # Create DataFrame
    data = [(entry.date, 1) for entry in journal_entries]
    df = pd.DataFrame(data, columns=['date', 'count'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby('date').sum().reset_index()
    
    # Create calendar heatmap
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.dayofweek
    
    plt.figure(figsize=(15, 8))
    
    # Create pivot table for heatmap
    pivot = df.pivot_table(values='count', index='weekday', columns='day', fill_value=0)
    
    # Create heatmap
    sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.5, cbar_kws={'label': 'Journal Entries'})
    plt.title(f"Journal Activity Heatmap - User {user_id}", fontsize=16, fontweight='bold')
    plt.xlabel("Day of Month")
    plt.ylabel("Day of Week")
    plt.yticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    
    plt.tight_layout()
    path = f"static/journal_heatmap_{user_id}.png"
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return FileResponse(path, media_type="image/png")

@app.get("/api/wellness-dashboard/{user_id}", tags=["Visualizations"])
def wellness_dashboard(user_id: int):
    """Generate comprehensive wellness dashboard"""
    mood_entries = DatabaseManager.get_mood_entries(user_id)
    journal_entries = DatabaseManager.get_journal_entries(user_id)
    
    if not mood_entries and not journal_entries:
        raise HTTPException(status_code=404, detail="No wellness data found")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f"Wellness Dashboard - User {user_id}", fontsize=16, fontweight='bold')
    
    # Mood distribution
    if mood_entries:
        mood_scores = [entry.mood_score for entry in mood_entries]
        axes[0, 0].hist(mood_scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title("Mood Score Distribution")
        axes[0, 0].set_xlabel("Mood Score")
        axes[0, 0].set_ylabel("Frequency")
    
    # Activity over time
    if journal_entries:
        journal_dates = [entry.date for entry in journal_entries]
        journal_df = pd.DataFrame({'date': journal_dates, 'count': 1})
        journal_df['date'] = pd.to_datetime(journal_df['date'])
        daily_counts = journal_df.groupby('date').count().reset_index()
        
        axes[0, 1].plot(daily_counts['date'], daily_counts['count'], marker='o')
        axes[0, 1].set_title("Daily Journal Activity")
        axes[0, 1].set_xlabel("Date")
        axes[0, 1].set_ylabel("Journal Entries")
        axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Wellness scores (simulated categories)
    categories = ['Sleep', 'Exercise', 'Mindfulness', 'Nutrition', 'Social']
    scores = [7, 6, 8, 7, 5]  # These could be calculated from user data
    
    axes[1, 0].bar(categories, scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    axes[1, 0].set_title("Wellness Categories")
    axes[1, 0].set_ylabel("Score")
    axes[1, 0].set_ylim(0, 10)
    
    # Recent mood trend
    if mood_entries and len(mood_entries) > 7:
        recent_moods = mood_entries[:7]  # Last 7 entries
        recent_dates = [entry.date for entry in recent_moods]
        recent_scores = [entry.mood_score for entry in recent_moods]
        
        axes[1, 1].plot(recent_dates, recent_scores, marker='o', color='green')
        axes[1, 1].set_title("Recent Mood Trend (Last 7 entries)")
        axes[1, 1].set_xlabel("Date")
        axes[1, 1].set_ylabel("Mood Score")
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    path = f"static/wellness_dashboard_{user_id}.png"
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return FileResponse(path, media_type="image/png")

# Keep the original wellness scores endpoint for backward compatibility
@app.get("/api/wellness-scores", tags=["Visualizations"])
def wellness_scores_chart():
    """Generate wellness score comparison chart"""
    scores = {
        'Sleep': 7,
        'Exercise': 5,
        'Mindfulness': 6,
        'Nutrition': 8,
        'Social': 4
    }
    df = pd.DataFrame({'Category': list(scores.keys()), 'Score': list(scores.values())})
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df['Category'], df['Score'], color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.title("Wellness Score Comparison", fontsize=16, fontweight='bold')
    plt.ylabel("Score")
    plt.ylim(0, 10)
    
    # Add value labels on bars
    for bar, score in zip(bars, df['Score']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(score), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    path = "static/wellness_scores.png"
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    return FileResponse(path, media_type="image/png")