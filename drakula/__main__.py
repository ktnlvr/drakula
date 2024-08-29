import dotenv
from pprint import pprint

from drakula.db import Database, Airport, GameDatabaseFacade

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)
    airports = game.fetch_random_airports(5, "OC")
    pprint(airports)
