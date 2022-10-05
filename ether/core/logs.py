from typing import Optional
from discord import Embed, Member

from ether.core.constants import Colors
from ether.core.utils import Utils


class EtherLogs:
    def base_log(
        self, member: Member, author_id: int, channel_id: int, reason: Optional[str]
    ):
        embed = Embed()
        embed.set_author(
            name=f"[{self}] {member.name}#{member.discriminator}",
            icon_url=Utils.get_avatar_url(member),
        )

        embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
        embed.add_field(name="Moderator", value=f"<@{author_id}>", inline=True)
        embed.add_field(name="Channel", value=f"<#{channel_id}>", inline=True)
        embed.add_field(name="Reason", value=reason or "No reason.", inline=True)
        return embed

    def kick(self, author_id: int, channel_id: int, reason: Optional[str]):
        embed = EtherLogs.base_log("KICK", self, author_id, channel_id, reason)
        embed.colour = Colors.KICK
        return embed

    def ban(self, author_id: int, channel_id: int, reason: Optional[str]):
        embed = EtherLogs.base_log("BAN", self, author_id, channel_id, reason)
        embed.description = "[`[unban]`](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
        embed.colour = Colors.BAN
        return embed
