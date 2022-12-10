import asyncio
from typing import List, Optional, Literal

from beanie import Document, init_beanie
from beanie.operators import AddToSet
from discord import ApplicationContext, Guild as GuildModel
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
            if user:
                return user

            return await Database.User.create(user_id)

        @staticmethod
        async def get_or_none(user_id: int):
            user = await User.find_one(User.id == user_id)
            if user:
                return user

            return None

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
            log.info(f"Creating guild user (user id: {user_id}, guild id: {guild_id})")

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
                GuildUser.user_id == user_id, GuildUser.guild_id == guild_id
            )
            if user:
                return user

            return None

        @staticmethod
        async def get_all(guild_id: int, max: int = 100):
            users = await GuildUser.find(GuildUser.guild_id == guild_id).to_list(max)
            if users:
                return users

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
    class ReactionRole:
        @staticmethod
        async def create(message_id: int, guild_id: int, options: List, _type: int = 0):
            reaction = ReactionRole(
                message_id=message_id, guild_id=guild_id, options=options, type=_type
            )

            await reaction.insert()
            log.info(f"Creating reaction role (message id: {message_id})")

            return await Database.ReactionRole.get_or_none(message_id)

        @staticmethod
        async def get_or_create(
            message_id: int,
            guild_id: int,
            options: Optional[List] = None,
            type: int = 0,
        ):
            reaction = await Database.ReactionRole.get_or_none(message_id)
            if reaction:
                return reaction

            return await Database.ReactionRole.create(
                message_id, guild_id, options, type
            )

        @staticmethod
        async def get_or_none(message_id: int):
            reaction = await ReactionRole.find_one(
                ReactionRole.message_id == message_id
            )
            if reaction:
                return reaction

            return None

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
        async def create(message_id: int, guild_id: int, playlist_link: str):
            playlist = Playlist(
                message_id=message_id, guild_id=guild_id, playlist_link=playlist_link
            )

            await playlist.insert()
            log.info(f"Creating playlist (message id: {message_id})")

            return await Database.Playlist.get_or_none(message_id)

        @staticmethod
        async def get_or_create(message_id: int, guild_id: int):
            playlist = await Database.Playlist.get_or_none(message_id)
            if playlist:
                return playlist

            return await Database.Playlist.create(message_id, guild_id)

        @staticmethod
        async def get_or_none(message_id: int):
            playlist = await Playlist.find_one(Playlist.message_id == message_id)
            if playlist:
                return playlist

            return None

        @staticmethod
        async def guild_limit(guild_id: int) -> bool:
            if await Playlist.find(Playlist.guild_id == guild_id).count() >= 3:
                return False
            return True


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

    async def from_id(guild_id: int):
        return await Database.Guild.get_or_create(guild_id)

    async def from_guild_object(guild: GuildModel):
        return await Guild.from_id(guild.id)

    async def from_context(ctx: Context):
        return await Guild.from_id(ctx.guild.id)


class GuildUser(Document):
    class Settings:
        name = "guild_users"

    user_id: int
    guild_id: int
    description: str = ""
    exp: int = 0
    levels: int = 1

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
    background: int = 0

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
    guild_id: int = -1
    playlist_link: str

    async def from_id(message_id: int):
        return await Database.Playlist.get_or_none(message_id)

    async def from_message_object(message: MessageModel):
        return await Playlist.from_id(message.id)

    async def from_context(ctx: Context):
        return await Playlist.from_id(ctx.message.id)

    async def from_guild(guild_id: int):
        return await Playlist.find(Playlist.guild_id == guild_id)


class ReactionRoleOption(BaseModel):
    role_id: int
    reaction: str


class ReactionRole(Document):
    class Settings:
        name = "reaction_roles"

    message_id: int
    guild_id: int = -1
    options: List[ReactionRoleOption]
    _type: Literal[0, 1, 2, 3] = 0
    # 0 => normal
    # 1 => unique
    # 2 => verify
    # 3 => drop

    async def from_id(message_id: int):
        return await Database.ReactionRole.get_or_none(message_id)

    async def from_message_object(message: MessageModel):
        return await ReactionRole.from_id(message.id)

    async def from_context(ctx: Context):
        return await ReactionRole.from_id(ctx.message.id)

    async def from_guild(guild_id: int):
        return await ReactionRole.find(ReactionRole.guild_id == guild_id)
