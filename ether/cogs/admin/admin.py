import logging
from typing import Optional
from discord import Embed, Member, User, slash_command
import discord
from discord.ext import commands
from humanize import precisedelta

from ether.core.bot_log import BanLog
from ether.core.constants import Colors
from ether.core.context import EtherEmbeds
from ether.core.db.client import Database
from ether.core.db.models import Guild
from ether.core.utils import Utils


class Admin(commands.Cog, name="admin"):
    def __init__(self, client):
        self.fancy_name = "Admin"
        self.client = client

    @slash_command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: User, *, reason: str = None):
        db_guild = self.client.db.get_guild(ctx.guild)

        if db_guild["logs"]["moderation"]["active"]:
            log_channel = ctx.guild.get_channel(
                db_guild["logs"]["moderation"]["channel_id"]
            )

            log_message = BanLog(
                client=self.client,
                user=member,
                author=ctx.author,
                channel=ctx.channel,
                log_channel=log_channel,
                reason=reason,
            )
            await log_message.send()

        try:
            if db_guild["logs"]["moderation"]["active"]:
                channel = ctx.guild.get_channel(
                    db_guild["logs"]["moderation"]["channel_id"]
                )
                if channel:
                    embed = Embed(
                        color=Colors.BAN,
                        description="[`[unban]`](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                    )
                    embed.set_author(
                        name=f"[BAN] {member.name}#{member.discriminator}",
                        icon_url=self.client.utils.get_avatar_url(member),
                    )
                    embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
                    embed.add_field(
                        name="Moderator", value=f"<@{ctx.author.id}>", inline=True
                    )
                    embed.add_field(
                        name="Channel", value=f"<#{ctx.channel.id}>", inline=True
                    )
                    embed.add_field(
                        name="Reason", value=reason or "No reason.", inline=True
                    )

                    await channel.send(embed=embed)

            await ctx.guild.ban(member)
            await ctx.repond("✅ Done")

        except Exception as e:
            print(e)
            await ctx.send_error(
                "Can't do that. Probably because I don't have the permissions for."
            )
            return

    @slash_command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason=None):
        guild = await Database.Guild.get_or_none(ctx.guild_id)
        
        if not guild:
            ctx.respond(embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"), delete_after=5)

        try:
            await ctx.guild.kick(member)
            if guild.logs and guild.logs.moderation:
                if guild.logs.moderation.enabled:
                    channel = ctx.guild.get_channel(
                        guild.logs.moderation.channel_id
                    )
                    if channel:
                        embed = Embed(color=Colors.KICK)
                        embed.set_author(
                            name=f"[KICK] {member.name}#{member.discriminator}",
                            icon_url=Utils.get_avatar_url(member),
                        )
                        embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
                        embed.add_field(
                            name="Moderator", value=f"<@{ctx.author.id}>", inline=True
                        )
                        embed.add_field(
                            name="Channel", value=f"<#{ctx.channel.id}>", inline=True
                        )
                        embed.add_field(
                            name="Reason", value=reason or "No reason.", inline=True
                        )
                        await channel.send(embed=embed)
            return await ctx.respond("✅ Done")
        except discord.errors.Forbidden:
            await ctx.respond(
                embed=EtherEmbeds.error("Can't do that. Probably because I don't have the permissions for.")
            )

    @slash_command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = Embed(description=f"Deleted {len(deleted) - 1} message(s).")
        embed.colour = Colors.SUCCESS
        await ctx.respond(embed=embed, delete_after=5)

    @slash_command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, cooldown: int):
        await ctx.channel.edit(slowmode_delay=cooldown)
        if cooldown == 0:
            await ctx.respond(f"✅ Slowmode disabled!")
            return
        await ctx.respond(f"✅ Slowmode set to `{precisedelta(cooldown)}`!")

    @slash_command(name="logs")
    @commands.has_permissions(manage_channels=True)
    async def logs(self, ctx, active: bool, channel: Optional[discord.TextChannel] = None):
        
        if channel:
            res = await Database.Guild.Logs.Moderation.set(ctx.guild.id, active, channel.id)
        else:
            res = await Database.Guild.Logs.Moderation.set(ctx.guild.id, active)
            
        if not res:
            ctx.respond(embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"), delete_after=5)
            
        if active:
            return await ctx.respond(f"✅ Logs set enabled!")
        
        return await ctx.respond(f"✅ Logs set disabled!")