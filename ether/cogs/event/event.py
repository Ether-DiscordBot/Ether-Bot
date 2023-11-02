import os
import random

from discord import ApplicationContext, Embed, File, HTTPException, errors
from discord.ext import commands
import gitinfo

from ether import __version__
from ether.cogs.event.welcomecard import WelcomeCard
from ether.core.db.client import Database, Guild, GuildUser
from ether.core.logging import log
from ether.core.i18n import init_i18n
from ether.core.config import config
from ether.core.utils import EtherEmbeds
from ether.core.voice_client import EtherPlayer


class Event(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.set_activity()

        # self.client.dbl.submit_command()

        repo = gitinfo.get_git_info()

        log.info(
            f"""\n\n
         ____   _   _                  
        ( ,__\ ( )_ ( )                 
        | (_   | ,_)| |__     __   ____ 
        | ,_)  | |  |  _  \ /'__`\(  __)
        | (___ | |_ | | | |(  ___/| |   
        (____/ \__) (_) (_) \____)(_)

        Version:        {__version__}"""
            + (
                f"""
        Commit:         {repo["commit"][:7]}
        Commit Date:    {repo["author_date"]}
        Author:         {repo["author"]}
        Branch:         {repo["refs"]}
        """
                if repo
                else ""
            )
            + f"""
        Client Name:    {self.client.user.name}
        Client ID:      {self.client.user.id}
        Guild Count:    {len(self.client.guilds)}
        Global SC:      {config.bot.get('global')}
        """
        )

        await self.client.start_lavalink_node(init=True)

        init_i18n(self.client)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.join and guild.logs.join.enabled:
            channel = member.guild.get_channel(guild.logs.join.channel_id)

            if not channel.permissions_for(self.client.user).send_messages:
                return

            if guild.logs.join.image:
                card = WelcomeCard.create_card(member, member.guild)
                try:
                    return await channel.send(
                        file=File(fp=card, filename=f"welcome_{member.name}.png")
                    )
                except commands.MissingPermissions:
                    return
            await channel.send(
                guild.logs.join.message.format(user=member, guild=member.guild)
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.leave and guild.logs.leave.enabled:
            channel = member.guild.get_channel(guild.logs.leave.channel_id)
            try:
                await channel.send(
                    guild.logs.leave.message.format(user=member, guild=member.guild)
                )
            except commands.MissingPermissions:
                return

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if Database.client != None and ctx.guild:
            guild = await Guild.from_guild_object(ctx.guild)
            await GuildUser.from_member_object(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = await Database.GuildUser.add_exp(
                    ctx.author.id, ctx.guild.id, 4 * guild.exp_mult
                )
                if not new_level:
                    return
                if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
                    return
                if guild.logs and guild.logs.join and guild.logs.join.enabled:
                    await ctx.channel.send(
                        f"Congratulation <@{ctx.author.id}>, you just pass to level {new_level}!"
                    )

    @commands.Cog.listener()
    async def on_application_command_completion(self, ctx):
        if random.randint(1, 100) <= 1:
            embed = Embed(
                title="Support us (we need money)!",
                description="Ether is a free and open source bot, please vote for the bot on [Top.gg](https://top.gg/bot/985100792270819389) and consider supporting us on [Ko-fi](https://ko-fi.com/holycrusader)!\n"
                "(we only need 7$ per month to keep the bot running)",
                color=0x2F3136,
            )

            if not ctx.channel.can_send():
                return

            await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def remove_cog(self, ctx: ApplicationContext, extension):
        log.info(f"Removed cog: {extension}")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, error):
        ignored = (
            commands.NoPrivateMessage,
            commands.DisabledCommand,
            commands.CheckFailure,
            commands.CommandNotFound,
            commands.UserInputError,
            HTTPException,
            errors.NotFound,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.errors.CommandOnCooldown):
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    f"This command is on cooldown, please retry in `{error.retry_after:.2f}s`."
                ),
                ephemeral=True,
            )

        if (
            isinstance(error, RuntimeError)
            and error.args[0]
            == "Websocket is not connected but attempted to listen, report this."
        ):
            player: EtherPlayer = ctx.guild.voice_client

            if player:
                log.error(
                    f"Lavalink Runtime error with node {player.node.label}({player.node.host}:{player.node.port})"
                )
                log.error(f"\t => Available: {player.node.available}")
                log.error(f"\t => Uptime: {player.node.stats.uptime}")

        await ctx.respond(
            embed=EtherEmbeds.error(
                description=f"An error occured while executing this command, please retry later.\n If the problem persist, please contact the support.\n\n Error: `{error.__class__.__name__}({error})`"
            ),
            ephemeral=True,
        )

        log.error(f"Error on command {ctx.command}")
        log.error(f" => Selected options: {ctx.selected_options}")
        raise error
