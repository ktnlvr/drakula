import dotenv

from drakula.db import Database

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    print(db.single_query("select * from flight_game.airport"))
