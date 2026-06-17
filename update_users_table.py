# update_users_table.py

import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN phone TEXT"
    )
except Exception as e:
    print(e)

try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN linkedin TEXT"
    )
except Exception as e:
    print(e)

conn.commit()
conn.close()

print("Database Updated")