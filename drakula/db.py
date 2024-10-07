import os
from typing import TypeVar, Callable, Optional, Union

from mysql.connector import connect

from .debug import get_dev_seed
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
        :param query: The query to be sent to the database for the result
        :param model: The function to produce the final object for each row of the query. Receives each
        associated column as a keyword argument.
        :returns: a list with `model` applied to each element
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        return list_map(cursor.fetchall(), model)
class GameDatabaseFacade:
    def __init__(self, db):
        self.db = db
        self._continents = list()
        self._continents = self.db.multi_query(
            "select distinct continent from airport", kwarg_id("continent")
        )

    def fetch_random_airports(
            self,
            amount: int = 1,
            continent: Optional[str] = None,
        *,
        seed: Optional[int] = None,
    ) -> list[Airport]:
        """
        :param amount: Amount of random airports to generate
        :param continent: Continent to select the airports from, All continents if None
        :param seed: Seed for the random number generator. Calling a function with the same parameters and a fixed
        seed produces the same result.
        :returns: A list of Airport objects
        """
        seed = seed or get_dev_seed()
        continent = continent or "EU"
        if continent and continent not in self._continents:
            raise Exception(f"Continent `{continent}` does not exist")
        query = f"select * from airport"
        if continent:
            query += f" where airport.continent = '{continent}'"
        query += f" order by RAND({'' if seed is None else seed}) limit {amount}"
        return list_map(self.db.multi_query(query), Airport)


def create_database_facade() -> GameDatabaseFacade:
    """
    :returns: An established database connection based on environmental variables.
    """
    host = os.getenv("DRAKULA_HOST") or "127.0.0.1"
    port = os.getenv("DRAKULA_PORT") or 3306
    user = os.getenv("DRAKULA_USER")
    password = os.getenv("DRAKULA_PASSWORD")

    db = Database(host, port, user, password)
    return GameDatabaseFacade(db)
