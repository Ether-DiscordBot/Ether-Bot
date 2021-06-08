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

    def get_user(self, user):
        if not user.bot:
            db_user = self.db.users.find_one({"user_id": user.id})
            if db_user:
                return db_user
            else:
                return self.create_user(user)
        else:
            return False

    def create_user(self, user):
        if not user.bot:
            self.db.users.insert_one(
                {
                    "user_id": user.id,
                    "user_datas": {
                        "premium": False,
                        "exp": 0,
                        "birthday": None,
                        "sexe": None,
                    },
                }
            )

    def update_user(self, user, key, value):
        db_user.update_one({"user_id": user.id}, {"$set": {key, value}})

    def find_user_data(self, user, key):
        db_user = self.get_user(user)
        return db_user.get(key)

    def add_exp(self, user, value):
        db_user = self.get_user(user)
        self.update_user(user, "exp", self.find_user_data(user, "exp") + value)
