from PIL.Image import new
import pymongo
import os
import bson
from .utils import MathsLevels

__all__ = ["Database"]

class Database(object):
    def __init__(self):
        client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
        self.db = client["dbot"]
        if self.db:
            print("\n\tMongoDB logged")
            for collection in self.db.list_collection_names():
                print(f"\t > Find collection => {collection}")

        self.default_prefix = os.getenv("BASE_PREFIX")
    
    """
        Guilds
    """

    def get_guild(self, guild, cd=5):
        db_guild = self.db.guilds.find_one({"id": bson.Int64(guild.id)})
        if db_guild:
            return db_guild
        if cd > 0:
            return self.create_guild(guild, cd-1)
        return

    def create_guild(self, guild, cd=5):
        self.db.guilds.insert_one(
            {
                "id": bson.Int64(guild.id),
                "prefix": self.default_prefix,
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
                        "active": False
                    },
                    "moderation": {
                        "channel_id": guild.text_channels[0].id,
                        "active": False,
                    }
                }
            }
        )

        return self.get_guild(guild, cd)

    def update_guild(self, guild, key, value):
        self.db.guilds.update_one({"id": bson.Int64(guild.id)}, {"$set": {key: value}})
        
    """
        Guild Users
    """

    def get_guild_user(self, guild, user, cd=5):
        if user.bot:
            return
        db_user = self.db.guild_users.find_one({"guild_id": bson.Int64(guild.id), "id": bson.Int64(user.id)})
        if db_user:
            return db_user
        if cd > 0:
            return self.create_guild_user(guild, user, cd-1)
        return

    def create_guild_user(self, guild, user, cd=5):
        self.db.guild_users.insert_one(
            {
                "id": bson.Int64(user.id),
                "guild_id": bson.Int64(guild.id),
                "exp": 0,
                "levels": 1
            }
        )
        return self.get_guild_user(guild, user, cd)

    def add_exp(self, guild, user, amount):
        dbuser = self.get_guild_user(guild, user)
        if dbuser:
            new_exp=dbuser['exp']+amount
            new_level_exp=new_exp-MathsLevels.level_to_exp(dbuser['levels']+1)
            if new_level_exp >= 0:
                self.db.guild_users.update_one({"guild_id": bson.Int64(guild.id), "id": bson.Int64(user.id)}, {"$set": {"exp": new_level_exp, "levels": dbuser['levels']+1}})
                return dbuser['levels']+1
            self.db.guild_users.update_one({"guild_id": bson.Int64(guild.id), "id": bson.Int64(user.id)}, {"$set": {"exp": new_exp}})
            return -1
        return

    """
        Users
    """
    
    def get_user(self, user, cd=5):
        if user.bot:
            return
        db_user = self.db.users.find_one({"id": bson.Int64(user.id)})
        if db_user:
            return db_user
        if cd > 0:
            return self.create_user(user, cd-1)
        return

    def create_user(self, user, cd=5):
        self.db.users.insert_one(
            {
                "id": bson.Int64(user.id),
                "card": {
                    "color": "A3C7F7",
                    "id": 0
                    },
            }
        )
        return self.get_user(user, cd)

    def update_user(self, user, key, value):
        self.db.users.update_one({"id": bson.Int64(user.id)}, {"$set": {key: value}})
    
    
    """
        Playlists
    """
    
    def get_playlist(self, guild, message):
        db_playlist = self.db.playlists.find_one({"message_id": bson.Int64(message.id), "guild_id": bson.Int64(guild.id)})
        if db_playlist:
            return db_playlist
        return

    def create_playlist(self, guild, message, url):
        self.db.playlists.insert_one(
            {
                "url": bson.Int64(url),
                "guild_id": bson.Int64(guild.id),
                "message_id": bson.Int64(message.id)
            }
        )
        return self.get_playlist(guild, message)

    def update_playlist(self, guild, message, key, value):
        self.db.playlists.update_one({"message_id": bson.Int64(message.id), "guild_id": bson.Int64(guild.id)}, {"$set": {key: value}})
    
    def delete_playlist(self, id):
        self.db.playlists.delete_one({"message_id": bson.Int64(id)})