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
        

async def init_database():
    load_dotenv()
    Database.client = AsyncIOMotorClient(os.getenv("MONGO_DB_URI")).dbot
    
    # FIXME
    await init_beanie(
        database=Database.client, document_models=[models.Guild, models.GuildUser, models.User]
    )
    
    models._database = Database

asyncio.run(init_database())