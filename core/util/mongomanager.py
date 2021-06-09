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
            db_user = self.db.users.find_one({"id": user.id})
            if db_user["username"] != user.name:
                self.update_user(user, "username", user.name)
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
                    "id": user.id,
                    "username": user.name,
                    "premium": False,
                    "exp": 0,
                }
            )

    def update_user(self, user, key, value):
        self.db.users.update_one({"id": user.id}, {"$set": {key: value}})

    def add_exp(self, user, value):
        if not user.bot:
            db_user = self.get_user(user)
            self.update_user(user, "exp", db_user["exp"] + value)

    def set_birthday(self, user, birthday):
        self.update_user(user, "birthday", birthday)

    def set_sex(self, user, sex):
        self.update_user(user, "sex", sex)
