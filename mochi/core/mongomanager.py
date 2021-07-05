import pymongo
import os


class Database(object):
    def __init__(self):
        self._uri = os.getenv("MONGODB_URI")
        self.client = pymongo.MongoClient(self._uri)
        self.db = self.client["dbot"]
        self.default_prefix = os.getenv("BASE_PREFIX")

        print("\n\tMongoDB logged")

        for collection in self.db.list_collection_names():
            print(f"\tFind collection => {collection}")

    def get_guild(self, guild):
        db_guild = self.db.guilds.find_one({"id": str(guild.id)})
        if db_guild:
            return db_guild
        return self.create_guild(guild)

    def create_guild(self, guild):
        self.db.guilds.insert_one(
            {
                "id": str(guild.id),
                "prefix": [self.default_prefix],
                "premium": False,
                "logs": {
                    "join": {
                        "channel_id": guild.text_channels[0].id,
                        "message": "Welcome to {user.name} !",
                        "active": False,
                        "private": False,
                    },
                    "leave": {
                        "channel_id": guild.text_channels[0].id,
                        "message": "{user.name} is gone",
                        "active": False,
                        "private": False,
                    },
                    "moderation": {
                        "channel_id": guild.text_channels[0].id,
                        "active": False,
                    }
                }
            }
        )

        return self.get_guild(guild)

    def update_guild(self, guild, key, value):
        self.db.guilds.update_one({"id": str(guild.id)}, {"$set": {key: value}})

    def get_user(self, guild, user):
        user = self.db.users.find_one({"gid": str(guild.id), "uid": str(user.id)})
        if user:
            return user
        return self.create_guild(guild, user)

    def create_user(self, guild, user):
        self.db.users.insert_one(
            {
                "gid": str(guild.id),
                "uid": str(user.id),
                "exp": 0,
                "lvl": 0
            }
        )
        return self.get_user(guild, user)

    def update_user(self, guild, user, key, value):
        self.db.users.update_one({"gid": str(guild.id), "uid": str(user.id)}, {"$set": {key: value}})
