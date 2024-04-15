import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def create_user(self, user_id):
        """
        Creates a new user in the database.
        :param user_id:
        :return:
        """
        with self.connection:
            result = self.cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            return result

    def check_user(self, user_id):
        """
        Checks if a user exists in the database.
        :param user_id:
        :return:
        """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,)).fetchone()
            return False if result is None else True
