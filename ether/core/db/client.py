import asyncio
from typing import List, Optional, Literal

from beanie import Document, init_beanie
from beanie.operators import AddToSet
from discord import Guild as GuildModel
from discord import Member as MemberModel
from discord import Message as MessageModel
from discord import User as UserModel
from discord.ext.commands import Context
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from ether.core.utils import LevelsHandler
from ether.core.logging import log


class Database:

    client = None

    class User:
        @staticmethod
        async def create(user_id: int):
            user = User(id=user_id)

            await user.insert()
            log.info(f"Creating user (id: {user_id})")

            return await Database.User.get_or_none(user_id)

        @staticmethod
        async def get_or_create(user_id: int):
            user = await Database.User.get_or_none(user_id)
            return user or await Database.User.create(user_id)

        @staticmethod
        async def get_or_none(user_id: int):
            user = await User.find_one(User.id == user_id)
            return user or None

    class Guild:
        @staticmethod
        async def create(guild_id: int):
            guild = Guild(id=guild_id)

            await guild.insert()
            log.info(f"Creating guild (id: {guild_id})")

            return await Database.Guild.get_or_none(guild_id)

        @staticmethod
        async def get_or_create(guild_id: int):
            guild = await Database.Guild.get_or_none(guild_id)
            return guild or await Database.Guild.create(guild_id)

        @staticmethod
        async def get_or_none(guild_id: int):
            guild = await Guild.find_one(Guild.id == guild_id)
            return guild or None

    class GuildUser:
        @staticmethod
        async def create(user_id: int, guild_id: int):
            user = GuildUser(user_id=user_id, guild_id=guild_id)

            await user.insert()
            log.info(f"Creating guild user (user id: {user_id}, guild id: {guild_id})")

            return await Database.GuildUser.get_or_none(user_id, guild_id)

        @staticmethod
        async def get_or_create(user_id: int, guild_id: int):
            user = await Database.GuildUser.get_or_none(user_id, guild_id)
            return user or await Database.GuildUser.create(user_id, guild_id)

        @staticmethod
        async def get_or_none(user_id: int, guild_id: int):
            user = await GuildUser.find_one(
                GuildUser.user_id == user_id, GuildUser.guild_id == guild_id
            )
            return user or None

        @staticmethod
        async def get_all(guild_id: int, max: int = 100):
            users = await GuildUser.find(GuildUser.guild_id == guild_id).to_list(max)
            return users or None

        @staticmethod
        async def add_exp(user_id, guild_id, amount):
            user = await Database.GuildUser.get_or_create(user_id, guild_id)

            if not user:
                return

            new_exp = user.exp + amount
            next_level = LevelsHandler.get_next_level(user.levels)
            if next_level <= new_exp:
                await user.set(
                    {
                        GuildUser.exp: new_exp - next_level,
                        GuildUser.levels: user.levels + 1,
                    }
                )
                return user.levels

            await user.set({GuildUser.exp: new_exp})

    @staticmethod
    class ReactionRole:
        @staticmethod
        async def create(message_id: int, options: List, _type: int = 0):
            reaction = ReactionRole(message_id=message_id, options=options, type=_type)

            await reaction.insert()
            log.info(f"Creating reaction role (message id: {message_id})")

            return await Database.ReactionRole.get_or_none(message_id)

        @staticmethod
        async def get_or_create(
            message_id: int, options: Optional[List] = None, type: int = 0
        ):
            reaction = await Database.ReactionRole.get_or_none(message_id)
            return reaction or await Database.ReactionRole.create(
                message_id, options, type
            )

        @staticmethod
        async def get_or_none(message_id: int):
            reaction = await ReactionRole.find_one(
                ReactionRole.message_id == message_id
            )
            return reaction or None

        @staticmethod
        async def update_or_create(message_id: int, option, _type: int = 0):
            reaction = await Database.ReactionRole.get_or_none(message_id)
            if reaction:
                return await reaction.update({"$push": {ReactionRole.options: option}})

            return await Database.ReactionRole.create(message_id, [option], _type)

        class ReactionRoleOption:
            @staticmethod
            def create(role_id: int, reaction: str):
                return ReactionRoleOption(role_id=role_id, reaction=reaction)

    class Playlist:
        @staticmethod
        async def create(message_id: int, playlist_link: str):
            playlist = Playlist(message_id=message_id, playlist_link=playlist_link)

            await playlist.insert()
            log.info(f"Creating playlist (message id: {message_id})")

            return await Database.Playlist.get_or_none(message_id)

        @staticmethod
        async def get_or_create(message_id: int):
            playlist = await Database.Playlist.get_or_none(message_id)
            return playlist or await Database.Playlist.create(message_id)

        @staticmethod
        async def get_or_none(message_id: int):
            playlist = await Playlist.find_one(Playlist.message_id == message_id)
            return playlist or None


def init_database(db_uri):
    Database.client = AsyncIOMotorClient(db_uri).dbot

    asyncio.run(
        init_beanie(
            database=Database.client,
            document_models=[Guild, GuildUser, User, ReactionRole, Playlist],
        )
    )


"""
    MODELS
"""


class JoinLog(BaseModel):
    channel_id: int
    message: str = "Welcome to <@{user.id}>!"
    enabled: bool = False
    private: bool = False
    image: bool = False


class LeaveLog(BaseModel):
    channel_id: int
    message: str = "<@{user.id}> is gone!"
    enabled: bool = False


class ModerationLog(BaseModel):
    channel_id: int
    enabled: bool = False


class Logs(BaseModel):
    join: Optional[JoinLog] = None
    leave: Optional[LeaveLog] = None
    moderation: Optional[ModerationLog] = None


class Guild(Document):
    class Settings:
        name = "guilds"

    id: int
    logs: Optional[Logs] = None
    auto_role: Optional[int] = None
    music_channel_id: Optional[int] = None
    exp_mult: float = 1.0

    async def from_id(self):
        return await Database.Guild.get_or_create(self)

    async def from_guild_object(self):
        return await Guild.from_id(self.id)

    async def from_context(self):
        return await Guild.from_id(self.guild.id)


class GuildUser(Document):
    class Settings:
        name = "guild_users"

    user_id: int
    guild_id: int
    description: str = ""
    exp: int = 0
    levels: int = 1

    async def from_id(self, guild_id: int):
        return await Database.GuildUser.get_or_create(self, guild_id)

    async def from_member_object(self):
        return await GuildUser.from_id(self.id, self.guild.id)

    async def from_context(self):
        return await GuildUser.from_id(self.author.id, self.guild.id)


class User(Document):
    class Settings:
        name = "users"

    id: int
    description: Optional[str] = None
    card_color: int = 0xA5D799
    background: int = 0

    async def from_id(self):
        return await Database.User.get_or_create(self)

    async def from_user_object(self):
        return await User.from_id(self.id)

    async def from_context(self):
        return await User.from_id(self.author.id)


class Playlist(Document):
    class Settings:
        name = "playlists"

    message_id: int
    playlist_link: str

    async def from_id(self):
        return await Database.Playlist.get_or_none(self)

    async def from_message_object(self):
        return await ReactionRole.from_id(self.id)

    async def from_context(self):
        return await ReactionRole.from_id(self.message.id)


class ReactionRoleOption(BaseModel):
    role_id: int
    reaction: str


class ReactionRole(Document):
    class Settings:
        name = "reaction_roles"

    message_id: int
    options: List[ReactionRoleOption]
    _type: Literal[0, 1, 2, 3] = 0
    # 0 => normal
    # 1 => unique
    # 2 => verify
    # 3 => drop

    async def from_id(self):
        return await Database.ReactionRole.get_or_none(self)

    async def from_message_object(self):
        return await ReactionRole.from_id(self.id)

    async def from_context(self):
        return await ReactionRole.from_id(self.message.id)
