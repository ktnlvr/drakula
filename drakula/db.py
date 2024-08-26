import os
from mysql.connector import connect

class Database():
    def __init__(self):
        host = os.getenv("DRAKULA_HOST") or "127.0.0.1"
        port = os.getenv("DRAKULA_PORT") or 3306
        user = os.getenv("DRAKULA_USER")
        password = os.getenv("DARKULA_PASSWORD")
        self.connection = connect(host=host, port=port, user=user, password=password)

    def single_query(self, query: str) -> dict:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchone()

    def multi_query(self, query: str) -> list[dict]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
