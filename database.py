import sqlite3

def create_database():

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    phone TEXT,
    linkedin TEXT,
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

    # Resume Analysis Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_analysis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        filename TEXT,
        skills TEXT,
        strength INTEGER DEFAULT 1,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    try:
       cursor.execute(
        "ALTER TABLE resume_analysis ADD COLUMN strength INTEGER DEFAULT 1"
       )
    except:
     pass

    conn.commit()
    conn.close()

create_database()

print("Database Created Successfully!")