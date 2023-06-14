import sqlite3


connection = sqlite3.connect('data.db')

with connection:
    connection.execute("""
        CREATE TABLE HISTORY (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city_query TEXT,
            city_choice TEXT,
            hotels_count INTEGER,
            photo_count INTEGER
        )
    """)
