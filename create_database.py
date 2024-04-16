import sqlite3


def create_database() -> None:
    """
    Creates a database with table 'users'.
    """
    database = sqlite3.connect('users.db')
    cursor = database.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL
        )
    ''')

    database.commit()
    database.close()


create_database()
