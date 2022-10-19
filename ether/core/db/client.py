import asyncio
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from beanie import Document, init_beanie, TimeSeriesConfig
from discord import Guild as GuildModel
from discord import Member as MemberModel
from discord import Message as MessageModel
from discord import User as UserModel
from discord.ext.commands import Context
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from ether.core.utils import LevelsHandler


class Database:

    client = None

    class Guild:
        @staticmethod
        async def create(guild_id: int):
            guild = Guild(id=guild_id)

            await guild.insert()

            return await Database.Guild.get_or_none(guild_id)

        @staticmethod
        async def get_or_create(guild_id: int):
            guild = await Database.Guild.get_or_none(guild_id)
            if guild:
                return guild

            return await Database.Guild.create(guild_id)

        @staticmethod
        async def get_or_none(guild_id: int):
            guild = await Guild.find_one(Guild.id == guild_id)
            if guild:
                return guild

            return None

    class GuildUser:
        @staticmethod
        async def create(user_id: int, guild_id: int):
            user = GuildUser(user_id=user_id, guild_id=guild_id)

            await user.insert()

            return await Database.GuildUser.get_or_none(user_id, guild_id)

        @staticmethod
        async def get_or_create(user_id: int, guild_id: int):
            user = await Database.GuildUser.get_or_none(user_id, guild_id)
            if user:
                return user

            return await Database.GuildUser.create(user_id, guild_id)

        @staticmethod
        async def get_or_none(user_id: int, guild_id: int):
            user = await GuildUser.find_one(
                GuildUser.user_id == user_id and GuildUser.guild_id == guild_id
            )
            if user:
                return user

            return None

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
        async def warn(user_id, guild_id, reason):
            user = await Database.GuildUser.get_or_create(user_id, guild_id)

            if not user:
                return

            await user.update({"$push": {"warns": Warn(reason=reason)}})

    @staticmethod
    class ReactionRole:
        @staticmethod
        async def create(message_id: int, options: List):
            reaction = ReactionRole(message_id=message_id, options=options)

            await reaction.insert()

            return await Database.ReactionRole.get_or_none(message_id)

        @staticmethod
        async def get_or_create(message_id: int):
            reaction = await Database.ReactionRole.get_or_none(message_id)
            if reaction:
                return reaction

            return await Database.ReactionRole.create(message_id)

        @staticmethod
        async def get_or_none(message_id: int):
            reaction = await ReactionRole.find_one(
                ReactionRole.message_id == message_id
            )
            if reaction:
                return reaction

            return None

        class ReactionRoleOption:
            @staticmethod
            def create(role_id: int, reaction: str):
                return ReactionRoleOption(role_id=role_id, reaction=reaction)

    class Playlist:
        @staticmethod
        async def create(message_id: int, playlist_link: str):
            playlist = Playlist(message_id=message_id, playlist_link=playlist_link)

            await playlist.insert()

            return await Database.Playlist.get_or_none(message_id)

        @staticmethod
        async def get_or_create(message_id: int):
            playlist = await Database.Playlist.get_or_none(message_id)
            if playlist:
                return playlist

            return await Database.Playlist.create(message_id)

        @staticmethod
        async def get_or_none(message_id: int):
            playlist = await Playlist.find_one(Playlist.message_id == message_id)
            if playlist:
                return playlist

            return None


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

    async def from_id(guild_id: int):
        return await Database.Guild.get_or_create(guild_id)

    async def from_guild_object(guild: GuildModel):
        return await Guild.from_id(guild.id)

    async def from_context(ctx: Context):
        return await Guild.from_id(ctx.guild.id)


class Warn(BaseModel):
    reason: Optional[str] = None
    ts: datetime = Field(default_factory=datetime.now)


class GuildUser(Document):
    class Settings:
        name = "guild_users"

    user_id: int
    guild_id: int
    description: str = ""
    exp: int = 0
    levels: int = 1
    warns: List[Warn] = []

    async def from_id(user_id: int, guild_id: int):
        return await Database.GuildUser.get_or_create(user_id, guild_id)

    async def from_member_object(member: MemberModel):
        return await GuildUser.from_id(member.id, member.guild.id)

    async def from_context(ctx: Context):
        return await GuildUser.from_id(ctx.author.id, ctx.guild.id)


class User(Document):
    class Settings:
        name = "users"

    id: int
    description: Optional[str] = None
    card_color: int = 0xA5D799

    async def from_id(user_id: int):
        return await Database.User.get_or_create(user_id)

    async def from_user_object(user: UserModel):
        return await User.from_id(user.id)

    async def from_context(ctx: Context):
        return await User.from_id(ctx.author.id)


class Playlist(Document):
    class Settings:
        name = "playlists"

    message_id: int
    playlist_link: str

    async def from_id(message_id: int):
        return await Database.Playlist.get_or_none(message_id)

    async def from_message_object(message: MessageModel):
        return await ReactionRole.from_id(message.id)

    async def from_context(ctx: Context):
        return await ReactionRole.from_id(ctx.message.id)


class ReactionRoleOption(BaseModel):
    role_id: int
    reaction: str


class ReactionRole(Document):
    class Settings:
        name = "reaction_roles"

    message_id: int
    options: List[ReactionRoleOption]

    async def from_id(message_id: int):
        return await Database.ReactionRole.get_or_none(message_id)

    async def from_message_object(message: MessageModel):
        return await ReactionRole.from_id(message.id)

    async def from_context(ctx: Context):
        return await ReactionRole.from_id(ctx.message.id)
