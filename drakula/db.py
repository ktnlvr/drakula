import os
from mysql.connector import connect
from typing import TypeVar, Callable, Optional

from drakula.utils import list_map, kwarg_id
from drakula.models import Airport

T = TypeVar("T")

class Database:
    def __init__(self):
        host = os.getenv("DRAKULA_HOST") or "127.0.0.1"
        port = os.getenv("DRAKULA_PORT") or 3306
        user = os.getenv("DRAKULA_USER")
        password = os.getenv("DRAKULA_PASSWORD")

        self.connection = connect(host=host, port=port, user=user, password=password)

    def single_query(self, query: str, model: Callable[[...], T] = dict) -> Optional[dict | T]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        if ret := cursor.fetchone():
            return model(ret)

    def multi_query(self, query: str, model: Callable[[...], T] = dict) -> list[dict | T]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        return list_map(cursor.fetchall(), model)

class GameDatabaseFacade:
    def __init__(self, db):
        self.db = db
        self.db.single_query("use flight_game;")

        self.continents = list()
        self.update_caches()

    def fetch_random_airports(self, amount: int | None = None, continent: str | None = None):
        amount = amount or 1
        continent = continent or "EU"
        if continent not in self.continents:
            raise Exception(f"Continent `{continent}` does not exist")
        query = f"select * from airport where airport.continent = '{continent}' order by RAND() limit {amount}"
        return list_map(self.db.multi_query(query), Airport)

    def update_caches(self):
        self.continents = self.db.multi_query("select distinct continent from airport", kwarg_id("continent"))
