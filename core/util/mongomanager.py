import pymongo
import os


class Database(object):
    def __init__(self):
        self._uri = os.getenv("MONGODB_URI")
        self.client = pymongo.MongoClient(self._uri)
        self.db = self.client["dbot"]

        print("\n\tMongoDB logged")

        for collection in self.db.list_collection_names():
            print(f"\tFind collection => {collection}")
