import asyncio
import datetime
from typing import Any, Dict, List, Literal, Optional

import discord
from beanie import Document, init_beanie
from discord import Guild as GuildModel
from discord import Member as MemberModel
from discord import Message as MessageModel
from discord import User as UserModel
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

import ether.core.db.events
from ether.core.logging import log
from ether.core.utils import LevelsHandler


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
            return user if user else await Database.User.create(user_id)

        @staticmethod
        async def get_or_none(user_id: int):
            user = await User.find_one(User.id == user_id)
            return user if user else None

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
            return guild if guild else await Database.Guild.create(guild_id)

        @staticmethod
        async def get_or_none(guild_id: int):
            guild = await Guild.find_one(Guild.id == guild_id)
            return guild if guild else None

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
            return user if user else await Database.GuildUser.create(user_id, guild_id)

        @staticmethod
        async def get_or_none(user_id: int, guild_id: int):
            user = await GuildUser.find_one(
                GuildUser.user_id == user_id, GuildUser.guild_id == guild_id
            )
            return user if user else None

        @staticmethod
        async def get_all(guild_id: int, max: int = 100):
            users = await GuildUser.find(GuildUser.guild_id == guild_id).to_list(max)
            return users if users else None

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
            reaction = ReactionRole(
                message_id=message_id, options=options, type=_type
            )

            await reaction.insert()
            log.info(f"Creating reaction role (message id: {message_id})")

            return await Database.ReactionRole.get_or_none(message_id)

        @staticmethod
        async def get_or_create(
            message_id: int,
            options: Optional[List] = None,
            type: int = 0,
        ):
            reaction = await Database.ReactionRole.get_or_none(message_id)
            if reaction:
                return reaction

            return await Database.ReactionRole.create(
                message_id, options, type
            )

        @staticmethod
        async def get_or_none(message_id: int):
            reaction = await ReactionRole.find_one(
                ReactionRole.message_id == message_id
            )
            return reaction if reaction else None

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
        async def create(message_id: int, guild_id: int, playlist_id: str):
            playlist = Playlist(
                message_id=message_id, guild_id=guild_id, playlist_id=playlist_id
            )

            await playlist.insert()
            log.info(f"Playlist created: (id: {playlist_id}, guild id: {guild_id})")

            return await Database.Playlist.get_or_none(message_id)

        @staticmethod
        async def get_or_create(message_id: int, guild_id: int, playlist_id: str):
            playlist = await Database.Playlist.get_or_none(message_id)
            if playlist:
                return playlist

            return await Database.Playlist.create(message_id, guild_id, playlist_id)

        @staticmethod
        async def get_or_none(message_id: int):
            playlist = await Playlist.find_one(Playlist.message_id == message_id)
            return playlist if playlist else None

        @staticmethod
        async def guild_limit(guild_id: int) -> bool:
            return not await Playlist.find(Playlist.guild_id == guild_id).count() >= 10

    class BotStatistic:
        class CommandUsage:

            @staticmethod
            async def get_or_create(command_name: str):
                command = await Database.BotStatistic.CommandUsage.get_or_none(command_name)
                if command:
                    return command

                command = CommandUsage(id=command_name)

                await command.insert()
                log.info(f"CommandUsage created ({command_name})")

                return await Database.BotStatistic.CommandUsage.get_or_none(command_name)

            @staticmethod
            async def get_or_none(command_name: str):
                command = await CommandUsage.find_one(CommandUsage.id == command_name)
                return command if command else None

            @staticmethod
            async def register_usage(command_name: str):
                command: CommandUsage = await Database.BotStatistic.CommandUsage.get_or_create(command_name)

                year = datetime.datetime.now().year
                month = datetime.datetime.now().month

                key = f"({year}, {month})"

                # It's ugly but it works
                if not command.month_usage.get(key):
                    command.month_usage[key] = 1
                else:
                    command.month_usage[key] += 1

                await command.save_changes()


def init_database(db_uri):
    Database.client = AsyncIOMotorClient(db_uri).dbot

    asyncio.run(
        init_beanie(
            database=Database.client,
            document_models=[Guild, GuildUser, User, ReactionRole, Playlist, CommandUsage],
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


class Birthday(BaseModel):
    enable: bool = False
    channel_id: Optional[int] = None
    hour: int = 9


class Guild(Document):
    class Settings:
        name = "guilds"

    id: int
    logs: Optional[Logs] = None
    auto_role: Optional[int] = None
    music_channel_id: Optional[int] = None
    exp_mult: float = 1.0
    birthday: Birthday = Birthday()

    async def from_id(self):
        return await Database.Guild.get_or_create(self)

    async def from_guild_object(self):
        return await Guild.from_id(self.id)

    async def from_interaction(self):
        return await Guild.from_id(self.guild.id)


class Date(BaseModel):
    day: int
    month: int
    year: Optional[int] = None

    def __str__(self):
        dt = datetime.date(year=self.year or 1900, month=self.month, day=self.day)

        return dt.strftime("%d %B %Y") if self.year else dt.strftime("%d %B")


class GuildUser(Document):
    class Settings:
        name = "guild_users"

    user_id: int
    guild_id: int
    description: str = ""
    exp: int = 0
    levels: int = 1
    birthday: Optional[Date] = None

    async def from_id(self, guild_id: int):
        return await Database.GuildUser.get_or_create(self, guild_id)

    async def from_member_object(self):
        return await GuildUser.from_id(self.id, self.guild.id)

    async def from_context(self):
        return await GuildUser.from_id(self.user.id, self.guild.id)


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
        return await User.from_id(self.user.id)


class Playlist(Document):
    class Settings:
        name = "playlists"

    message_id: int
    guild_id: int = -1
    playlist_link: Optional[str] = None  # deprecated
    playlist_id: Optional[str] = None

    async def from_id(self):
        return await Database.Playlist.get_or_none(self)

    async def from_message_object(self):
        return await Playlist.from_id(self.id)

    async def from_context(self):
        return await Playlist.from_id(self.message.id)

    def from_guild(self):
        return Playlist.find(Playlist.guild_id == self)


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

    async def from_id(self):
        return await Database.ReactionRole.get_or_none(self)

    async def from_message_object(self):
        return await ReactionRole.from_id(self.id)

    async def from_context(self):
        return await ReactionRole.from_id(self.message.id)

    def from_guild(self):
        return ReactionRole.find(ReactionRole.guild_id == self)

class CommandUsage(Document):
    class Settings:
        name = "command_usage"
        use_state_management = True

    id: str
    month_usage: Dict[Any, int] = {} # {(year, month): count}

    async def register_usage(self):
        return await Database.BotStatistic.CommandUsage.register_usage(self)
