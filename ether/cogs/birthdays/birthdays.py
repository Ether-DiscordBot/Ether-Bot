import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import (
    Option,
    OptionChoice,
    ApplicationContext,
    Member,
    SlashCommandGroup,
    Embed,
    TextChannel,
)
from discord.ext import commands
import pymongo
from ether.core.constants import Emoji

from ether.core.db import Guild, GuildUser
from ether.core.db.client import Date
from ether.core.utils import EtherEmbeds
from ether.core.logging import log


def date_time_left(user):
    date = user.birthday
    now = datetime.date.today()
    obj_date = datetime.date(year=now.year, month=date.month, day=date.day)
    if obj_date < now:
        obj_date = datetime.date(year=now.year + 1, month=date.month, day=date.day)

    return (obj_date - now).days


class Birthday(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.help_icon = Emoji.BIRTHDAY

        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.birthdays_loop, "cron", minute=0)
        scheduler.start()

    async def birthdays_loop(self):
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

    birthday = SlashCommandGroup("birthday", "Birthdays commands!")

    @birthday.command(name="remember")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remember(
        self,
        ctx: ApplicationContext,
        date: Option(str, "Date (dd/mm/yyyy) or (dd/mm)"),
        user: Optional[Member] = None,
    ):
        """Remember a birthday"""
        user = user or ctx.author
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
            return await ctx.respond(
                embed=EtherEmbeds.error("Invalid date format! (dd/mm/yyyy) or (dd/mm)")
            )

        db_user = await GuildUser.from_id(user_id=user.id, guild_id=ctx.guild.id)
        await db_user.set(
            {
                GuildUser.birthday: Date(
                    day=date[0], month=date[1], year=date[2] if len(date) == 3 else None
                )
            }
        )

        await ctx.respond(
            embed=EtherEmbeds.success(
                description=f"{user.mention}'s birthday is well noted for the **{db_user.birthday}**!"
            )
        )

    @birthday.command(name="forget")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def forget(self, ctx: ApplicationContext, user: Member):
        """Forget a birthday"""
        db_user = await GuildUser.from_id(user.id)
        await db_user.set({GuildUser.birthday: None})

        await ctx.respond(
            embed=EtherEmbeds.success(
                f"I won't remember {user.mention}'s birthday anymore!"
            )
        )

    @birthday.command(name="show")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def show(self, ctx: ApplicationContext, user: Member):
        """Show a user's birthday"""
        db_user: GuildUser = await GuildUser.from_id(user.id, ctx.guild.id)

        if not db_user.birthday:
            return await ctx.respond(
                embed=EtherEmbeds.error("This user doesn't have a birthday set!")
            )

        await ctx.respond(
            embed=Embed(
                description=f"{user.mention}'s birthday is the `{db_user.birthday}`!"
            )
        )

    @birthday.command(name="list")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def list(self, ctx: ApplicationContext):
        """List the 10 upcoming birthdays"""
        users = await GuildUser.find(
            {GuildUser.guild_id: ctx.guild.id, GuildUser.birthday: {"$exists": True}}
        ).to_list()
        if not users:
            return await ctx.respond("No birthdays found")

        users = sorted(users, key=date_time_left)[:10]

        embed = Embed(title=f"🎂 Upcoming birthdays")
        for user in users:
            embed.add_field(
                name=user.birthday, value=f"<@{user.user_id}>", inline=False
            )

        await ctx.respond(embed=embed)

    config = birthday.create_subgroup(
        name="config", description="Configure the birthday system"
    )

    @config.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def config_enable(self, ctx: ApplicationContext, enable: bool):
        """Enable or disable the birthday system"""

        guild = await Guild.from_id(ctx.guild.id)
        await guild.set({Guild.birthday.enable: enable})

        await ctx.respond(
            embed=EtherEmbeds.success(
                "Birthdays are now enabled\n*(Don't forget to set the channel and the hour!)*"
                if enable
                else "Birthdays are now disabled"
            )
        )

    @config.command(name="channel")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def config_channel(
        self, ctx: ApplicationContext, channel: Optional[TextChannel] = None
    ):
        """Set the channel where the bot will post the birthday messages"""
        channel = channel or ctx.channel

        guild = await Guild.from_id(ctx.guild.id)
        await guild.set({Guild.birthday.channel_id: channel.id})

        await ctx.respond(
            embed=EtherEmbeds.success(f"Set the birthday channel to {channel.mention}")
        )

    @config.command(name="time")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def config_time(
        self,
        ctx: ApplicationContext,
        hour: Option(
            int,
            name="hour",
            description="Happy Birthday Wishing Hour",
            choices=[OptionChoice(f"{h:02}:00", value=h) for h in range(0, 23)],
        ),
    ):
        """Set the hour when the bot will post the birthday messages"""

        guild = await Guild.from_id(ctx.guild.id)
        await guild.set({Guild.birthday.hour: hour})

        await ctx.respond(
            embed=EtherEmbeds.success(f"Birthdays will be posted at {hour}:00")
        )
