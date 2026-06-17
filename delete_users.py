import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute(
    "DELETE FROM users WHERE email=?",
    ("dhanvikmpgowda@gmail.com",)
)

conn.commit()
conn.close()

print("User deleted successfully!")