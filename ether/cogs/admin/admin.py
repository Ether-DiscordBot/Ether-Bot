from discord import Embed, User
from discord.ext import commands
from humanize import precisedelta

from ether.core.bot_log import BanLog
from ether.core.constants import Colors


class Admin(commands.Cog, name="admin"):
    def __init__(self, client):
        self.fancy_name = "Admin"
        self.client = client

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: User, *, reason: str = None):
        if not member:
            await ctx.send_error(f"Unknown **{member.name}** !")
            return

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

        except Exception as e:
            print(e)
            await ctx.send_error(
                "Can't do that. Probably because I don't have the permissions for."
            )
            return

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: User, *, reason=None):
        db_guild = self.client.db.get_guild(ctx.guild)
        if not member:
            embed = Embed(
                color=Colors.ERROR, description=f"Unknown **{member.name}** !"
            )
            return await ctx.send(embed=embed)

        try:
            if db_guild["logs"]["moderation"]["active"]:
                channel = ctx.guild.get_channel(
                    db_guild["logs"]["moderation"]["channel_id"]
                )
                if channel:
                    embed = Embed(color=Colors.KICK)
                    embed.set_author(
                        name=f"[KICK] {member.name}#{member.discriminator}",
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

                    await ctx.guild.kick(member)

                    await channel.send(embed=embed)
        except Exception:
            await ctx.send_error(
                "Can't do that. Probably because I don't have the " "permissions for."
            )
            return

    @commands.command(name="clear", aliases=["purge", "cleanup"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if not amount:
            await ctx.send_error(
                "Please indicate a number of messages to delete.", delete_after=5
            )
            return

        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = Embed(description=f"Deleted {len(deleted) - 1} message(s).")
        embed.colour = Colors.SUCCESS
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, cd: int):
        await ctx.channel.edit(slowmode_delay=cd)
        if cd == 0:
            await ctx.send(f"✅ Slowmode disabled!")
            return
        await ctx.send(f"✅ Slowmode set to `{precisedelta(cd)}`!")
