import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute(
    """
    UPDATE users
    SET is_admin = 1
    WHERE email = ?
    """,
    ("dhanvikmpgowda@gmail.com",)
)

conn.commit()
conn.close()

print("Admin assigned successfully!")