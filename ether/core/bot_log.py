from discord import Embed, User, TextChannel
import logging

__all__ = ["BanLog"]

class LogMessage():
    def __init__(self,
                 client,
                 action: str,
                 user: User,
                 author: User,
                 channel: TextChannel,
                 log_channel: TextChannel,
                 reason: str = None
                 ):
        
        embed = Embed()
        embed.set_author(name=f"[{action}] {user.name}#{user.discriminator}", icon_url=client.utils.get_avatar_url(user))
        embed.add_field(name="User", value=f"<@{user.id}>", inline=True)
        embed.add_field(name="Moderator", value=f"<@{author.id}>", inline=True)
        embed.add_field(name="Channel", value=f"<#{channel.id}>", inline=True)
        embed.add_field(name="Reason", value=reason or "No reason.", inline=True)
        
        self.embed = embed
    
    async def send(self):
        await self.channel.send(embed=self.embed)

class BanLog(LogMessage):
    def __init__(self,
                 client,
                 user: User,
                 author: User,
                 channel: TextChannel,
                 log_channel: TextChannel,
                 reason: str = None):
        super().__init__(client=client, action="BAN", user=user, author=author, channel=channel, reason=reason)
        self.embed.description="[`[unban]`](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
        