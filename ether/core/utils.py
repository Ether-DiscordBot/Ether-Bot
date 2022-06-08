import math

from discord import Embed, Member

from ether.core.constants import Colors


class LevelsHandler:
    def get_level(level: int, exp):
        return int(math.sqrt(max(LevelsHandler.level_to_exp(level) + exp, 1)) * 0.2)

    def get_next_level(level: int):
        return 50 * pow(level, 2)


class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"


class EtherEmbeds:
    def error(message):
        return Embed(description=message, colour=Colors.ERROR)


class EtherLogs:
    def base_log(type: str, member: Member, author_id: int, channel_id: int, reason: str):
        embed = Embed()
        embed.set_author(
            name=f"[{type}] {member.name}#{member.discriminator}",
            icon_url=Utils.get_avatar_url(member),
        )
        embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
        embed.add_field(
            name="Moderator", value=f"<@{author_id}>", inline=True
        )
        embed.add_field(
            name="Channel", value=f"<#{channel_id}>", inline=True
        )
        embed.add_field(
            name="Reason", value=reason or "No reason.", inline=True
        )
        return embed
        
    def kick(member: Member, author_id: int, channel_id: int, reason: str):
        embed = EtherLogs.base_log("KICK", member, author_id, channel_id, reason)
        embed.colour = Colors.KICK
        return embed
            
    def ban(member: Member, author_id: int, channel_id: int, reason: str):
        embed = EtherLogs.base_log("BAN", member, author_id, channel_id, reason)
        embed.description =  "[`[unban]`](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
        embed.colour = Colors.BAN
        return embed
