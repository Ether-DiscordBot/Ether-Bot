import pymongo

import os
from dotenv import load_dotenv

load_dotenv()

class Database(object):
    USER = os.getenv('MONGO_DB_USER')
    PASS = os.getenv('MONGO_DB_PASS')
    DB = "dbot"

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(f"mongodb+srv://{Database.USER}:{Database.PASS}"
                             f"@cluster0.lkufy.mongodb.net/<dbname>?retryWrites=true&w=majority")
        Database.DATABASE = client[Database.DB]
