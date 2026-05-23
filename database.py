import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS tasks (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    status TEXT NOT NULL,

    priority TEXT,

    due_date TEXT
)
''')

conn.close()

print("Database created successfully!")