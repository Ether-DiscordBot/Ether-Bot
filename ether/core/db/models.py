import os

from typing import List, Optional
from discord import Guild as GuildModel
from discord import User as UserModel
from discord.ext.commands import Context
from beanie import Document
from pydantic import BaseModel

_database = None


class JoinLog(BaseModel):
    channel_id: Optional[int] = None
    message: str = "Welcome to {user.name}!"
    enabled: bool = False
    private: bool = False
    image: bool = False


class LeaveLog(BaseModel):
    channel_id: Optional[int] = None
    message: str = "{user.name} is gone!"
    enabled: bool = False


class ModerationLog(BaseModel):
    channel_id: Optional[int] = None
    enabled: bool = False


class Logs(BaseModel):
    join: Optional[JoinLog] = None
    leave: Optional[LeaveLog] = None
    moderation: Optional[ModerationLog] = None


class Guild(Document):
    id: int
    prefix: Optional[str] = os.getenv("BASE_PREFIX")
    logs: Logs
    auto_role: Optional[int] = None
    welcome_channel: Optional[int] = None
    welcome_card_enalbed: bool = False
    welcome_card_type: int = 0

    class DocumentMeta:
        collection_name = "guilds"

    async def from_id(guild_id: int):
        return await _database.Guild.get_or_create(guild_id)

    async def from_guild_object(guild: GuildModel):
        return await Guild.from_id(guild.id)

    async def from_context(ctx: Context):
        return await Guild.from_id(ctx.guild.id)


class GuildUser(Document):
    id: int
    guild_id: int
    description: str = ""
    exp: int = 0
    levels: int = 0

    class DocumentMeta:
        collection_name = "guild_users"

    async def from_id(user_id: int, guild_id: int):
        return await _database.GuildUser.get_or_create(user_id, guild_id)

    async def from_user_object(user: UserModel):
        return await GuildUser.from_id(user.id, user.guild.id)

    async def from_context(ctx: Context):
        return await GuildUser.from_id(ctx.author.id, ctx.guild.id)


class User(Document):
    id: int
    description: Optional[str] = None
    card_color: int = 0xa5d799

    class DocumentMeta:
        collection_name = "users"

    async def from_id(user_id: int):
        return await _database.User.get_or_create(user_id)

    async def from_user_object(user: UserModel):
        return await User.from_id(user.id)

    async def from_context(ctx: Context):
        return await User.from_id(ctx.author.id)


class Playlist(Document):
    message_id: int
    playlist_link: str

    class DocumentMeta:
        collection_name = "playlists"


class ReactionRoleOption(BaseModel):
    role_id: int
    reaction_id: int


class ReactionRole(Document):
    message_id: int
    options: List[ReactionRoleOption]

    class DocumentMeta:
        collection_name = "reaction_roles"
