from typing import List, Optional
from discord import Guild as GuildModel
from discord import User as UserModel
from discord import Member as MemberModel
from discord.ext.commands import Context
from beanie import Document
from pydantic import BaseModel

_database = None


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

    async def from_id(guild_id: int):
        return await _database.Guild.get_or_create(guild_id)

    async def from_guild_object(guild: GuildModel):
        return await Guild.from_id(guild.id)

    async def from_context(ctx: Context):
        return await Guild.from_id(ctx.guild.id)


class GuildUser(Document):
    class Settings:
        name = "guild_users"

    id: int
    guild_id: int
    description: str = ""
    exp: int = 0
    levels: int = 1


    async def from_id(user_id: int, guild_id: int):
        return await _database.GuildUser.get_or_create(user_id, guild_id)

    async def from_member_object(member: MemberModel):
        return await GuildUser.from_id(member.id, member.guild.id)

    async def from_context(ctx: Context):
        return await GuildUser.from_id(ctx.author.id, ctx.guild.id)


class User(Document):
    class Settings:
        name = "users"

    id: int
    description: Optional[str] = None
    card_color: int = 0xa5d799

    async def from_id(user_id: int):
        return await _database.User.get_or_create(user_id)

    async def from_user_object(user: UserModel):
        return await User.from_id(user.id)

    async def from_context(ctx: Context):
        return await User.from_id(ctx.author.id)


class Playlist(Document):
    class Settings:
        name = "playlists"

    message_id: int
    playlist_link: str


class ReactionRoleOption(BaseModel):
    role_id: int
    reaction_id: int


class ReactionRole(Document):
    class Settings:
        name = "reaction_roles"

    message_id: int
    options: List[ReactionRoleOption]
