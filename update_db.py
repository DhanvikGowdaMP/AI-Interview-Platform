import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE users
    ADD COLUMN is_admin INTEGER DEFAULT 0
    """)

    print("is_admin column added.")

except:
    print("Column already exists.")

conn.commit()
conn.close()