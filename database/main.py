import sqlite3
from typing import Tuple, List


class Database:
    def __init__(self, db_file: str) -> None:
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
                    user_id INTEGER PRIMARY KEY NOT NULL,
                    language VARCHAR(2),
                    received_ad INTEGER DEFAULT 0
                );
                '''
            )
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_hash TEXT NOT NULL UNIQUE,
                    availability INTEGER NOT NULL DEFAULT 1
                );
                '''
            )
            self.connection.commit()

    def save_user(self, user_id: int, language: str) -> sqlite3.Cursor:
        """
        Creates a new user in the database.
        """
        with self.connection:
            result = self.cursor.execute(
                '''
                INSERT INTO users (user_id, language)
                VALUES (?, ?);
                ''',
                (user_id, language)
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

    def save_account(self, api_hash: str) -> None:
        """
        Saves a new account to the database.
        """
        with self.connection:
            self.cursor.execute(
                '''
                INSERT INTO accounts (api_hash) VALUES (?);
                ''',
                (api_hash,)
            )
            self.connection.commit()

    def get_account_availability(self, api_hash: str) -> Tuple[int]:
        """
        Checks if account is in spamblock.
        """
        with self.connection:
            result = self.cursor.execute(
                '''
                SELECT availability
                FROM accounts
                WHERE api_hash=?;
                ''',
                (api_hash,)
            ).fetchone()
            return result

    def update_availability(self, api_hash: str, availability: int) -> None:
        """
        Updates availability column.
        """
        with self.connection:
            self.cursor.execute(
                '''
                UPDATE accounts
                SET availability=?
                WHERE api_hash=?;
                ''',
                (availability, api_hash,)
            )
            self.connection.commit()

    def list_pending_users(self) -> List[int]:
        """
        Lists all pending users.
        """
        with self.connection:
            result = self.cursor.execute(
                '''
                SELECT user_id
                FROM users
                WHERE received_ad = 0;
                '''
            ).fetchall()
            return [user_id[0] for user_id in result]

    def get_user_language(self, user_id: int) -> Tuple[str]:
        """
        Shows the user's language.
        """
        with self.connection:
            result = self.cursor.execute(
                '''
                SELECT language
                FROM users
                WHERE user_id = ?;
                ''',
                (user_id,)
            ).fetchone()
            return result

    def update_received_ad(self, user_id: int) -> None:
        """
        Marks the user as the one who received the ad.
        """
        with self.connection:
            self.cursor.execute(
                '''
                UPDATE users
                SET received_ad=1
                WHERE user_id = ?;
                ''',
                (user_id,)
            )
            self.connection.commit()
