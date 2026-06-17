import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute(
    "SELECT * FROM interview_results"
)

for row in cursor.fetchall():
    print(row)

conn.close()