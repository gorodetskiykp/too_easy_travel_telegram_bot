import sqlite3

connection = sqlite3.connect('data.db')

with connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS HISTORY (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            command TEXT,
            hotels TEXT
        )
    """)
