import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS interview_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    score TEXT,
    evaluation TEXT,
    interview_date TEXT
)
""")

conn.commit()
conn.close()

print("Interview Results Table Created")