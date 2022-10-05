import asyncio
from typing import List, Optional

from beanie import Document, init_beanie
from discord import Guild as GuildModel
from discord import Member as MemberModel
from discord import Message as MessageModel
from discord import User as UserModel
from discord.ext.commands import Context
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

try:
    from ether.core.utils import LevelsHandler

    levels_handler_import = True
except ImportError:
    levels_handler_import = False


class Database:

    client = None

    class Guild:
        async def create(self):
            guild = Guild(id=self)

            await guild.insert()

            return await Database.Guild.get_or_none(self)

        async def get_or_create(self):
            guild = await Database.Guild.get_or_none(self)
            return guild or await Database.Guild.create(self)

        async def get_or_none(self):
            guild = await Guild.find_one(Guild.id == self)
            return guild or None

        class Logs:
            class Moderation:
                async def set(self, enabled: bool, channel_id: Optional[int] = None):
                    guild = await Database.Guild.get_or_none(self)

                    if not guild:
                        return None

                    if channel_id:
                        moderation_logs = ModerationLog(
                            channel_id=channel_id, enabled=enabled
                        )
                    elif guild.logs and guild.logs.moderation:
                        moderation_logs = ModerationLog(
                            channel_id=guild.logs.moderation.channel_id, enabled=enabled
                        )

                    else:
                        return None
                    if guild.logs:
                        await guild.set({Guild.logs.moderation: moderation_logs})
                    else:
                        await guild.set({Guild.logs: Logs(moderation=moderation_logs)})

                    return True

    class GuildUser:
        async def create(self, guild_id: int):
            user = GuildUser(id=self, guild_id=guild_id)

            await user.insert()

            return await Database.GuildUser.get_or_none(self, guild_id)

        async def get_or_create(self, guild_id: int):
            user = await Database.GuildUser.get_or_none(self, guild_id)
            return user or await Database.GuildUser.create(self, guild_id)

        async def get_or_none(self, guild_id: int):
            user = await GuildUser.find_one(
                GuildUser.id == self and GuildUser.guild_id == guild_id
            )

            return user or None

        async def add_exp(self, guild_id, amount):
            if not levels_handler_import:
                return

            user = await Database.GuildUser.get_or_none(self, guild_id)

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

    class ReactionRole:
        async def create(self, options: List):
            reaction = ReactionRole(self=self, options=options)

            await reaction.insert()

            return await Database.ReactionRole.get_or_none(self)

        async def get_or_create(self):
            reaction = await Database.ReactionRole.get_or_none(self)
            return reaction or await Database.ReactionRole.create(self)

        async def get_or_none(self):
            reaction = await ReactionRole.find_one(ReactionRole.message_id == self)
            return reaction or None

        class ReactionRoleOption:
            def create(self, reaction: str):
                return ReactionRoleOption(self=self, reaction=reaction)

    class Playlist:
        async def create(self, playlist_link: str):
            playlist = Playlist(self=self, playlist_link=playlist_link)

            await playlist.insert()

            return await Database.Playlist.get_or_none(self)

        async def get_or_create(self):
            playlist = await Database.Playlist.get_or_none(self)
            return playlist or await Database.Playlist.create(self)

        async def get_or_none(self):
            playlist = await Playlist.find_one(Playlist.message_id == self)
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
    message: str = "Welcome to {user.name}!"
    enabled: bool = False
    private: bool = False
    image: bool = False


class LeaveLog(BaseModel):
    channel_id: int
    message: str = "{user.name} is gone!"
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
    logs: Logs = None
    auto_role: Optional[int] = None
    music_channel_id: Optional[int] = None

    async def from_id(self):
        return await Database.Guild.get_or_create(self)

    async def from_guild_object(self):
        return await Guild.from_id(self.id)

    async def from_context(self):
        return await Guild.from_id(self.guild.id)


class GuildUser(Document):
    class Settings:
        name = "guild_users"

    id: int
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

    async def from_id(self):
        return await Database.ReactionRole.get_or_none(self)

    async def from_message_object(self):
        return await ReactionRole.from_id(self.id)

    async def from_context(self):
        return await ReactionRole.from_id(self.message.id)
