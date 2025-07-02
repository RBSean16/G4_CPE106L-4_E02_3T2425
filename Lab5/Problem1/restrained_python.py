import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('ColonialAdventureTours.db')
cursor = conn.cursor()
conn.set_trace_callback(print)

# --- Ensure Tables Exist ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS GUIDE (
    GUIDE_NUM INTEGER PRIMARY KEY AUTOINCREMENT,
    LAST_NAME TEXT,
    FIRST_NAME TEXT,
    ADDRESS TEXT,
    CITY TEXT,
    STATE TEXT,
    POSTAL_CODE TEXT,
    PHONE_NUM TEXT,
    HIRE_DATE TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS CLASS (
    CLASS_NUM INTEGER PRIMARY KEY AUTOINCREMENT,
    CLASS_DESC TEXT,
    MAX_PEOPLE INTEGER,
    CLASS_FEE REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS CLASS_ASSIGNMENT (
    CLASS_NUM INTEGER,
    CLASS_DATE TEXT UNIQUE,  -- Enforces only one class per day
    GUIDE_NUM INTEGER,
    PRIMARY KEY (CLASS_NUM, CLASS_DATE, GUIDE_NUM),
    FOREIGN KEY (CLASS_NUM) REFERENCES CLASS(CLASS_NUM),
    FOREIGN KEY (GUIDE_NUM) REFERENCES GUIDE(GUIDE_NUM)
)
""")

# --- Insert Dummy Data If Tables Are Empty ---
cursor.execute("SELECT COUNT(*) FROM GUIDE")
if cursor.fetchone()[0] == 0:
    guides = [
        ("Stone", "Alex"), ("Rivera", "Dana"), ("Brooks", "Jamie"),
        ("Ng", "Taylor"), ("Cruz", "Jordan")
    ]
    cursor.executemany("""
        INSERT INTO GUIDE (LAST_NAME, FIRST_NAME, ADDRESS, CITY, STATE, POSTAL_CODE, PHONE_NUM, HIRE_DATE)
        VALUES (?, ?, '123 Trail Ave', 'Outdooria', 'EX', '11111', '555-0000', '2024-06-01')
    """, guides)

cursor.execute("SELECT COUNT(*) FROM CLASS")
if cursor.fetchone()[0] == 0:
    classes = [
        ("Backcountry Navigation", 10, 65.00),
        ("River Safety Basics", 12, 55.50),
        ("Mountain Biking Intro", 8, 70.25)
    ]
    cursor.executemany("""
        INSERT INTO CLASS (CLASS_DESC, MAX_PEOPLE, CLASS_FEE)
        VALUES (?, ?, ?)
    """, classes)

# --- Assign One Class Per Day with Random Guide ---
cursor.execute("SELECT CLASS_NUM FROM CLASS")
class_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT GUIDE_NUM FROM GUIDE")
guide_ids = [row[0] for row in cursor.fetchall()]

assignment_dates = set()
assignments = []

today = datetime.today()

for i in range(len(class_ids)):
    # ensure unique dates
    while True:
        days_ahead = random.randint(1, 30)
        new_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        if new_date not in assignment_dates:
            assignment_dates.add(new_date)
            break
    class_id = class_ids[i]
    guide_id = random.choice(guide_ids)
    assignments.append((class_id, new_date, guide_id))

cursor.executemany("""
    INSERT INTO CLASS_ASSIGNMENT (CLASS_NUM, CLASS_DATE, GUIDE_NUM)
    VALUES (?, ?, ?)
""", assignments)

# --- Output Scheduled Assignments ---
cursor.execute("""
    SELECT CLASS.CLASS_DESC, CLASS_ASSIGNMENT.CLASS_DATE,
           GUIDE.FIRST_NAME || ' ' || GUIDE.LAST_NAME AS GUIDE_NAME
    FROM CLASS_ASSIGNMENT
    JOIN CLASS ON CLASS.CLASS_NUM = CLASS_ASSIGNMENT.CLASS_NUM
    JOIN GUIDE ON GUIDE.GUIDE_NUM = CLASS_ASSIGNMENT.GUIDE_NUM
    ORDER BY CLASS_ASSIGNMENT.CLASS_DATE
""")

print("\nScheduled Classes with Assigned Guides:\n")
for row in cursor.fetchall():
    print("{} on {} — Instructor: {}".format(row[0], row[1], row[2]))

conn.commit()
conn.close()
