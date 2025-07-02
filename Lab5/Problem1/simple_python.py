import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('ColonialAdventureTours.db')
cursor = conn.cursor()
conn.set_trace_callback(print)  # Debug output for SQL

# --------- Ensure Required Tables Exist ---------
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
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS CLASS (
    CLASS_NUM INTEGER PRIMARY KEY AUTOINCREMENT,
    CLASS_DESC TEXT,
    MAX_PEOPLE INTEGER,
    CLASS_FEE REAL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS CLASS_ASSIGNMENT (
    CLASS_NUM INTEGER,
    CLASS_DATE TEXT,
    GUIDE_NUM INTEGER,
    PRIMARY KEY (CLASS_NUM, CLASS_DATE, GUIDE_NUM),
    FOREIGN KEY (CLASS_NUM) REFERENCES CLASS(CLASS_NUM),
    FOREIGN KEY (GUIDE_NUM) REFERENCES GUIDE(GUIDE_NUM)
);
""")

# --------- Insert Dummy Guide Data ---------
guides = [
    ("Anderson", "Casey"),
    ("Taylor", "Morgan"),
    ("Lee", "Jordan"),
    ("Martinez", "Riley"),
    ("Nguyen", "Drew")
]
cursor.executemany("""
    INSERT INTO GUIDE (LAST_NAME, FIRST_NAME, ADDRESS, CITY, STATE, POSTAL_CODE, PHONE_NUM, HIRE_DATE)
    VALUES (?, ?, '123 Main St', 'Cityville', 'ST', '12345', '555-1234', '2023-01-01')
""", guides)

# --------- Insert Dummy Class Data ---------
classes = [
    ("Intro to Hiking", 12, 49.99),
    ("Basic Paddling", 10, 59.99),
    ("Trail Biking 101", 8, 69.99),
    ("Advanced Kayaking", 6, 79.99)
]
cursor.executemany("""
    INSERT INTO CLASS (CLASS_DESC, MAX_PEOPLE, CLASS_FEE)
    VALUES (?, ?, ?)
""", classes)

# --------- Assign Random Guides to Classes on Random Dates ---------
cursor.execute("SELECT CLASS_NUM FROM CLASS")
class_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT GUIDE_NUM FROM GUIDE")
guide_ids = [row[0] for row in cursor.fetchall()]

base_date = datetime.today()
assignment_data = []

for class_id in class_ids:
    for i in range(3):  # 3 different dates
        random_days = random.randint(1, 30)
        class_date = (base_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        guide_id = random.choice(guide_ids)
        assignment_data.append((class_id, class_date, guide_id))

cursor.executemany("""
    INSERT INTO CLASS_ASSIGNMENT (CLASS_NUM, CLASS_DATE, GUIDE_NUM)
    VALUES (?, ?, ?)
""", assignment_data)

# --------- Display Class Assignments with Guides ---------
cursor.execute("""
    SELECT 
        C.CLASS_DESC,
        A.CLASS_DATE,
        G.FIRST_NAME || ' ' || G.LAST_NAME AS GUIDE_NAME
    FROM CLASS_ASSIGNMENT A
    JOIN CLASS C ON A.CLASS_NUM = C.CLASS_NUM
    JOIN GUIDE G ON A.GUIDE_NUM = G.GUIDE_NUM
    ORDER BY A.CLASS_DATE
""")

print("\nAssigned Classes:\n")
for row in cursor.fetchall():
    print("{} on {} - Guide: {}".format(row[0], row[1], row[2]))

# --------- Commit and Close ---------
conn.commit()
conn.close()
