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

    # USER

    def get_user(self, user, guild=None):
        if user.bot:
            return False
        db_user = self.db.users.find_one({"id": user.id})
        if guild:
            db_gm = self.get_guild_member(guild, user)
            if not db_gm:
                self.insert_member_guild(guild, user)
        if db_user:
            return db_user
        return self.create_user(user)

    def create_user(self, user):
        if not user.bot:
            self.db.users.insert_one(
                {
                    "id": user.id,
                    "exp": 0,
                    "level": 0,
                }
            )

        return self.get_user(user)

    def update_user(self, user, key, value):
        self.db.users.update_one({"id": user.id}, {"$set": {key: value}})

    def add_exp(self, user, guild, value):
        if not user.bot:
            db_user = self.get_user(user, guild)
            db_gm = self.get_guild_member(guild, user)
            self.update_user(user, "exp", db_user["exp"] + value)
            self.update_guild_member(guild, user, "exp", db_gm["exp"] + value)

    def set_birthday(self, user, birthday):
        self.update_user(user, "birthday", birthday)

    def set_sex(self, user, sex):
        self.update_user(user, "sex", sex)

    # GUILD

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
                    },
                },
                "members": [],
            }
        )

        return self.get_guild(guild)

    def update_guild(self, guild, key, value):
        self.db.guilds.update_one({"id": str(guild.id)}, {"$set": {key: value}})

    def insert_member_guild(self, guild, user):
        members_array = self.get_guild(guild)["members"]
        members_array.append({"id": user.id, "exp": 0, "level": 0})
        self.update_guild(guild, "members", members_array)

    def get_guild_member(self, guild, user):
        members = self.get_guild(guild)["members"]
        for m in members:
            if m["id"] == user.id:
                return m
        return None

    def update_guild_member(self, guild, user, key, value):
        self.db.guilds.update_one(
            {"id": str(guild.id), "members.id": user.id},
            {"$set": {("members.$." + key): value}},
        )
