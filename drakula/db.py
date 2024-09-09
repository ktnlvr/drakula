import os

from mysql.connector import connect
from typing import TypeVar, Callable, Optional, Union

from .utils import list_map, kwarg_id
from .models import Airport

T = TypeVar("T")


class Database:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.connection = connect(host=host, port=port, user=user, password=password)

    def single_query(
        self, query: str, model: Callable[[...], T] = dict
    ) -> Optional[Union[list, T]]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        if ret := cursor.fetchone():
            return model(ret)

    def multi_query(
        self, query: str, model: Callable[[...], T] = dict
    ) -> list[Union[list, T]]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        return list_map(cursor.fetchall(), model)


class GameDatabaseFacade:
    def __init__(self, db):
        self.db = db
        self.db.single_query("use flight_game;")

        self._continents = list()
        self.update_caches()

    def fetch_random_airports(
        self, amount: Optional[int] = None, continent: Optional[str] = None
    ) -> list[Airport]:
        amount = amount or 1
        continent = continent or "EU"
        if continent not in self._continents:
            raise Exception(f"Continent `{continent}` does not exist")
        query = f"select * from airport where airport.continent = '{continent}' order by RAND() limit {amount}"
        return list_map(self.db.multi_query(query), Airport)

    def update_caches(self):
        self._continents = self.db.multi_query(
            "select distinct continent from airport", kwarg_id("continent")
        )


def create_database_facade() -> GameDatabaseFacade:
    host = os.getenv("DRAKULA_HOST") or "127.0.0.1"
    port = os.getenv("DRAKULA_PORT") or 3306
    user = os.getenv("DRAKULA_USER")
    password = os.getenv("DRAKULA_PASSWORD")

    db = Database(host, port, user, password)
    return GameDatabaseFacade(db)
