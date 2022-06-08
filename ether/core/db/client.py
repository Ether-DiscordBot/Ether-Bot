import asyncio
import os
from typing import Optional
from beanie import init_beanie
import bson
from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient

from ether.core.utils import LevelsHandler
import ether.core.db.models as models

class Database:   

    client = None


    class Guild:
        async def create(guild_id: int):
            guild = models.Guild(id=guild_id)
            
            await guild.insert()
            
            return await Database.Guild.get_or_none(guild_id)
            
        async def get_or_create(guild_id: int):
            guild = await Database.Guild.get_or_none(guild_id)
            if guild:
                return guild
            
            return await Database.Guild.create(guild_id)
        
        async def get_or_none(guild_id: int):
            guild = await models.Guild.find_one(models.Guild.id == guild_id)
            if guild:
                return guild
            
            return None
        
        class Logs:
            class Moderation:
                async def set(guild_id: int, enabled: bool, channel_id: Optional[int] = None):
                    guild = await Database.Guild.get_or_none(guild_id)
                    
                    if not guild:
                        return None
                    
                    if channel_id:
                        moderation_logs = models.ModerationLog(channel_id=channel_id, enabled=enabled)
                    else:
                        if not (guild.logs and guild.logs.moderation):
                            return None
                        moderation_logs = models.ModerationLog(channel_id=guild.logs.moderation.channel_id, enabled=enabled)
                    
                    if guild.logs:
                        await guild.set({models.Guild.logs.moderation: moderation_logs})
                    else:
                        await guild.set({models.Guild.logs: models.Logs(moderation=moderation_logs)})
                        
                    return True
                    
                    
                    
    
    class GuildUser:
        async def create(user_id: int, guild_id: int):
            user = models.GuildUser(id=user_id, guild_id=guild_id)
            
            await user.insert()
            
            return await Database.GuildUser.get_or_none(user_id, guild_id)
            
        async def get_or_create(user_id: int, guild_id: int):
            user = await Database.GuildUser.get_or_none(user_id, guild_id)
            if user:
                return user
            
            return await Database.GuildUser.create(user_id, guild_id)
        
        async def get_or_none(user_id: int, guild_id: int):
            user = await models.GuildUser.find_one(models.GuildUser.id == user_id, models.GuildUser.guild_id == guild_id)
            if user:
                return user
            
            return None

        async def add_exp(user_id, guild_id, amount):
            user = await Database.GuildUser.get_or_none(user_id, guild_id)
            
            if not user:
                return
            
            new_exp = user.exp + amount
            next_level = LevelsHandler.get_next_level(user.levels)
            if next_level <= new_exp:
                await user.set({models.GuildUser.exp: new_exp - next_level, models.GuildUser.levels: user.levels + 1})
                return user.levels
            
            await user.set({models.GuildUser.exp: new_exp})
        
        
    def update_guild(self, guild, key, value):
        self.db.guilds.update_one({"id": bson.Int64(guild.id)}, {"$set": {key: value}})

    """
        Guild Users
    """

    def get_guild_user(self, guild, user, cd=5):
        if user.bot:
            return
        if db_user := self.db.guild_users.find_one(
            {"guild_id": bson.Int64(guild.id), "id": bson.Int64(user.id)}
        ):
            return db_user
        if cd > 0:
            return self.create_guild_user(guild, user, cd - 1)
        return

    def create_guild_user(self, guild, user, cd=5):
        self.db.guild_users.insert_one(
            {
                "id": bson.Int64(user.id),
                "guild_id": bson.Int64(guild.id),
                "exp": 0,
                "levels": 1,
            }
        )
        return self.get_guild_user(guild, user, cd)

    """
        Users
    """

    def get_user(self, user, cd=5):
        if user.bot:
            return
        if db_user := self.db.users.find_one({"id": bson.Int64(user.id)}):
            return db_user
        if cd > 0:
            return self.create_user(user, cd - 1)
        return

    def create_user(self, user, cd=5):
        self.db.users.insert_one(
            {
                "id": bson.Int64(user.id),
                "card": {"color": "A3C7F7", "id": 0},
            }
        )
        return self.get_user(user, cd)

    def update_user(self, user, key, value):
        self.db.users.update_one({"id": bson.Int64(user.id)}, {"$set": {key: value}})

    """
        Playlists
    """

    def get_playlist(self, guild, message):
        if db_playlist := self.db.playlists.find_one(
            {
                "message_id": bson.Int64(message.id),
                "guild_id": bson.Int64(guild.id),
            }
        ):
            return db_playlist
        return

    def create_playlist(self, guild, message, url):
        self.db.playlists.insert_one(
            {
                "url": bson.Int64(url),
                "guild_id": bson.Int64(guild.id),
                "message_id": bson.Int64(message.id),
            }
        )
        return self.get_playlist(guild, message)

    def update_playlist(self, guild, message, key, value):
        self.db.playlists.update_one(
            {"message_id": bson.Int64(message.id), "guild_id": bson.Int64(guild.id)},
            {"$set": {key: value}},
        )

    def delete_playlist(self, id):
        self.db.playlists.delete_one({"message_id": bson.Int64(id)})


async def init_database():
    load_dotenv()
    Database.client = AsyncIOMotorClient(os.getenv("MONGO_DB_URI")).dbot
    
    # FIXME
    await init_beanie(
        database=Database.client, document_models=[models.Guild, models.GuildUser, models.User]
    )
    
    models._database = Database

asyncio.run(init_database())