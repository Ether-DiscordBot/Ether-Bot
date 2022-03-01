from discord import Embed, User
from discord.ext import commands

from ether import Color
from ether.core import BanLog


class Admin(commands.Cog, name="admin"):
    def __init__(self, client):
        self.fancy_name = "Admin"
        self.client = client

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: User, *, reason: str = None):
        if not member:
            embed = Embed(
                color=Color.ERROR, description=f"Unknown **{member.name}** !"
            )
            return await ctx.send(embed=embed)

        db_guild = self.client.db.get_guild(ctx.guild)

        if db_guild["logs"]["moderation"]["active"]:
            log_channel = ctx.guild.get_channel(db_guild["logs"]["moderation"]["channel_id"])

            log_message = BanLog(client=self.client, user=member, author=ctx.author, channel=ctx.channel,
                                 log_channel=log_channel, reason=reason)
            await log_message.send()

        try:
            if db_guild["logs"]["moderation"]["active"]:
                channel = ctx.guild.get_channel(db_guild["logs"]["moderation"]["channel_id"])
                if channel:
                    embed = Embed(color=Color.BAN,
                                  description="[`[unban]`](https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
                    embed.set_author(name=f"[BAN] {member.name}#{member.discriminator}",
                                     icon_url=self.client.utils.get_avatar_url(member))
                    embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
                    embed.add_field(name="Moderator", value=f"<@{ctx.author.id}>", inline=True)
                    embed.add_field(name="Channel", value=f"<#{ctx.channel.id}>", inline=True)
                    embed.add_field(name="Reason", value=reason or "No reason.", inline=True)

                    await channel.send(embed=embed)

            await ctx.guild.ban(member)

        except Exception as e:
            print(e)
            embed = Embed(
                color=Color.ERROR,
                description="Can't do that. Probably because I don't have the permissions for.",
            )
            return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: User, *, reason=None):
        db_guild = self.client.db.get_guild(ctx.guild)
        if not member:
            embed = Embed(
                color=Color.ERROR, description=f"Unknown **{member.name}** !"
            )
            return await ctx.send(embed=embed)

        try:
            if db_guild["logs"]["moderation"]["active"]:
                channel = ctx.guild.get_channel(db_guild["logs"]["moderation"]["channel_id"])
                if channel:
                    embed = Embed(color=Color.KICK)
                    embed.set_author(name=f"[KICK] {member.name}#{member.discriminator}",
                                     icon_url=self.client.utils.get_avatar_url(member))
                    embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
                    embed.add_field(name="Moderator", value=f"<@{ctx.author.id}>", inline=True)
                    embed.add_field(name="Channel", value=f"<#{ctx.channel.id}>", inline=True)
                    embed.add_field(name="Reason", value=reason or "No reason.", inline=True)

                    await ctx.guild.kick(member)

                    await channel.send(embed=embed)
        except Exception:
            embed = Embed(
                color=Color.ERROR,
                description="Can't do that. Probably because I don't have the "
                            "permissions for.",
            )
            return await ctx.send(embed=embed)

    @commands.command(name="clear", aliases=["purge", "cleanup"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if not amount:
            await ctx.send("Please specify a number.")
            return

        deleted = await ctx.channel.purge(limit=amount+1)
        await ctx.send(f'Deleted {len(deleted)-1} message(s).', delete_after=5)
