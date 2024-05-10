import sqlite3


class Database:
    def __init__(self, db_file: str):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        """
        Creates tables if they do not exist.
        """
        with self.connection:
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL
                );
                '''
            )
            self.connection.commit()

    def create_user(self, user_id: int) -> sqlite3.Cursor:
        """
        Creates a new user in the database.
        """
        with self.connection:
            result = self.cursor.execute(
                '''
                INSERT INTO users (user_id)
                VALUES (?);
                ''',
                (user_id,)
            )
            self.connection.commit()
            return result

    def check_user(self, user_id: int) -> bool:
        """
        Checks if a user exists in the database.
        """
        with self.connection:
            result = self.cursor.execute(
                '''
                SELECT *
                FROM users
                WHERE user_id=?;
                ''',
                (user_id,)
            ).fetchone()
            return False if result is None else True
