import datetime
from typing import Optional

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Member, TextChannel, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Context

from ether.core.constants import Emoji
from ether.core.db import Guild, GuildUser
from ether.core.db.client import Date
from ether.core.embed import Embed
from ether.core.logging import log


def date_time_left(user):
    date = user.birthday
    now = datetime.date.today()
    obj_date = datetime.date(year=now.year, month=date.month, day=date.day)
    if obj_date < now:
        obj_date = datetime.date(year=now.year + 1, month=date.month, day=date.day)

    return (obj_date - now).days


class Birthday(commands.GroupCog, name="birthday"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.help_icon = Emoji.BIRTHDAY

        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.birthdays_loop, "cron", minute=0)
        scheduler.start()

    config = app_commands.Group(
        name="config", description="Birthday related commands"
    )

    async def birthdays_loop(self):
        await self.client.wait_until_ready()

        log.debug("Checking birthdays...")
        now = datetime.datetime.now()
        guilds = (
            await Guild.find({Guild.birthday: {"$exists": True}})
            .find({Guild.birthday.enable: True})
            .find({Guild.birthday.channel_id: {"$exists": True}})
            .find({Guild.birthday.hour: now.hour})
            .to_list()
        )

        for guild in guilds:
            channel = self.client.get_channel(guild.birthday.channel_id)
            if channel is None:
                continue

            users = (
                await GuildUser.find({GuildUser.guild_id: guild.id})
                .find({GuildUser.birthday: {"$exists": True}})
                .find(
                    {
                        GuildUser.birthday.day: now.day,
                        GuildUser.birthday.month: now.month,
                    }
                )
                .to_list()
            )
            if not users:
                continue

            for user in users:
                age = f"({now.year - user.birthday.year})" if user.birthday.year else ""
                await channel.send(f"It's the birthday of <@{user.user_id}> {age} 🎂!")

    @app_commands.command(name="remember")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(date="Date (dd/mm/yyyy) or (dd/mm)")
    async def remember(
        self,
        interaction: discord.Interaction,
        date: str,
        user: Optional[Member] = None,
    ):
        """Remember a birthday"""
        user = user or interaction.user
        try:
            date = date.split("/")
            date = list(map(int, date))

            if len(date) < 2 and len(date) > 3:
                raise ValueError("Invalid date format")

            if date[0] > 31 or date[1] > 12:
                raise ValueError("Invalid date format")

            if len(date) == 3 and len(str(date[2])) != 4:
                raise ValueError("Invalid date format")
        except ValueError:
            return await interaction.response.send_message(
                embed=Embed.error(description="Invalid date format! (dd/mm/yyyy) or (dd/mm)")
            )

        db_user = await GuildUser.from_id(
            user_id=user.id, guild_id=interaction.guild.id
        )
        await db_user.set(
            {
                GuildUser.birthday: Date(
                    day=date[0], month=date[1], year=date[2] if len(date) == 3 else None
                )
            }
        )

        await interaction.response.send_message(
            embed=Embed.success(
                description=f"{user.mention}'s birthday is well noted for the **{db_user.birthday}**!"
            )
        )

    @app_commands.command(name="forget")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def forget(self, interaction: discord.Interaction, user: Member):
        """Forget a birthday"""
        db_user = await GuildUser.from_id(user.id)
        await db_user.set({GuildUser.birthday: None})

        await interaction.response.send_message(
            embed=Embed.success(description=f"I won't remember {user.mention}'s birthday anymore!")
        )

    @app_commands.command(name="show")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def show(self, interaction: discord.Interaction, user: Member):
        """Show a user's birthday"""
        db_user: GuildUser = await GuildUser.from_id(user.id, interaction.guild.id)

        if not db_user.birthday:
            return await interaction.response.send_message(
                embed=Embed.error(description="This user doesn't have a birthday set!")
            )

        await interaction.response.send_message(
            embed=Embed(
                description=f"{user.mention}'s birthday is the `{db_user.birthday}`!"
            )
        )

    @app_commands.command(name="list")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def list(self, interaction: discord.Interaction):
        """List the 10 upcoming birthdays"""
        users = await GuildUser.find(
            {
                GuildUser.guild_id: interaction.guild.id,
                GuildUser.birthday: {"$exists": True},
            }
        ).to_list()
        if not users:
            return await interaction.response.send_message("No birthdays found")

        users = sorted(users, key=date_time_left)[:10]

        embed = Embed(title=f"🎂 Upcoming birthdays")
        for user in users:
            embed.add_field(
                name=user.birthday, value=f"<@{user.user_id}>", inline=False
            )

        await interaction.response.send_message(embed=embed)

    @config.command(name="enable")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def config_enable(self, interaction: discord.Interaction, enable: bool):
        """Enable or disable the birthday system"""

        guild = await Guild.from_id(interaction.guild.id)
        await guild.set({Guild.birthday.enable: enable})

        await interaction.response.send_message(
            embed=Embed.success(
                description="Birthdays are now enabled\n*(Don't forget to set the channel and the hour!)*"
                if enable
                else "Birthdays are now disabled"
            )
        )

    @config.command(name="channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def config_channel(
        self, interaction: discord.Interaction, channel: Optional[TextChannel] = None
    ):
        """Set the channel where the bot will post the birthday messages"""
        channel = channel or interaction.channel

        guild = await Guild.from_id(interaction.guild.id)
        await guild.set({Guild.birthday.channel_id: channel.id})

        await interaction.response.send_message(
            embed=Embed.success(description=f"Set the birthday channel to {channel.mention}")
        )

    @config.command(name="time")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(hour="Happy Birthday Wishing Hour")
    @app_commands.choices(
        hour=[Choice(name=f"{h:02}:00", value=h) for h in range(0, 23)]
    )
    async def config_time(
        self,
        interaction: discord.Interaction,
        hour: Choice[int],
    ):
        """Set the hour when the bot will post the birthday messages"""

        guild = await Guild.from_id(interaction.guild.id)
        await guild.set({Guild.birthday.hour: hour})

        await interaction.response.send_message(
            embed=Embed.success(description=f"Birthdays will be posted at {hour}:00")
        )
