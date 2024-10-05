import os
from typing import TypeVar, Callable, Optional, Union

from mysql.connector import connect

from .models import Airport
from .utils import list_map, kwarg_id

T = TypeVar("T")


class Database:
    """
    A class which has all the methods needed for talking to the database with the query
    provided
    """
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.connection = connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="flight_game",
            autocommit=False,
        )

    def multi_query(
        self, query: str, model: Callable[[...], T] = dict
    ) -> list[Union[list, T]]:
        """
        Args:
            query: The query to be sent to the database for the result
            model: Optional argument which is callable function to change the data type
            from default dictionary to some other type

        Returns: dict by default but may return some other data type if the function is provided

        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        return list_map(cursor.fetchall(), model)

class GameDatabaseFacade:
    def __init__(self, db):
        self.db = db
        self._continents = list()
        self.update_caches()

    def fetch_random_airports(
        self,
        amount: Optional[int] = None,
        continent: Optional[str] = None,
        *,
        seed: Optional[int] = None,
    ) -> list[Airport]:
        """
        Args:
            amount: Amount of random airports to generate defaults to 1
            continent: Continent to generate from defaults to EU
            seed: Seed is randomness in the result

        Returns: A list of Airport object
        """
        amount = amount or 1
        continent = continent or "EU"
        if continent and continent not in self._continents:
            raise Exception(f"Continent `{continent}` does not exist")
        query = f"select * from airport"
        if continent:
            query += f" where airport.continent = '{continent}'"
        query += f" order by RAND({'' if seed is None else seed}) limit {amount}"
        return list_map(self.db.multi_query(query), Airport)

    def update_caches(self):
        self._continents = self.db.multi_query(
            "select distinct continent from airport", kwarg_id("continent")
        )


def create_database_facade() -> GameDatabaseFacade:
    """
    Returns:A object of GameDataBaseFacade
    """
    host = os.getenv("DRAKULA_HOST") or "127.0.0.1"
    port = os.getenv("DRAKULA_PORT") or 3306
    user = os.getenv("DRAKULA_USER")
    password = os.getenv("DRAKULA_PASSWORD")

    db = Database(host, port, user, password)
    return GameDatabaseFacade(db)
