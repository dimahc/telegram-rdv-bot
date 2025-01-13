import sqlite3
import threading

import config


class Database:
    def __init__(self):
        self.local = threading.local()
        self._create_table()

    def _get_connection(self):
        if not hasattr(self.local, "connection"):
            self.local.connection = sqlite3.connect(database=config.DATABASE_PATH)
            self.local.cursor = self.local.connection.cursor()
        return self.local.connection, self.local.cursor

    def _create_table(self):
        connection, cursor = self._get_connection()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY,
                date TEXT,
                time TEXT,
                location TEXT
            )
        """
        )
        connection.commit()

    def save_appointments(self, appointments):
        connection, cursor = self._get_connection()
        self._flush_db()
        cursor.executemany(
            """
            INSERT INTO appointments (date, time, location) VALUES (?, ?, ?)
        """,
            appointments,
        )
        connection.commit()

    def get_appointments(self):
        connection, cursor = self._get_connection()
        cursor.execute("SELECT date, time, location FROM appointments")
        return cursor.fetchall()

    def _flush_db(self):
        connection, cursor = self._get_connection()
        cursor.execute("DELETE FROM appointments")
        connection.commit()

    def close(self):
        if hasattr(self.local, "connection"):
            self.local.connection.close()
