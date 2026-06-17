import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(resume_analysis)")

for row in cursor.fetchall():
    print(row)

conn.close()