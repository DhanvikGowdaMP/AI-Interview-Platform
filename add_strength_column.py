import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE resume_analysis
ADD COLUMN strength INTEGER
""")

conn.commit()
conn.close()

print("Strength column added.")