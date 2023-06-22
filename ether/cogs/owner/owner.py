import os

from discord import SlashCommandGroup, File
from discord.ext import commands

from ether.cogs.event.welcomecard import WelcomeCard


class Owner(commands.Cog):
    LOGS_FILE_PATH = os.path.abspath("logs.log")

    def __init__(self, client):
        self.client = client

        self.help_icon = ""
        self.big_icon = ""

    owner = SlashCommandGroup(name="owner", description="Owner commands")

    @owner.command(name="logs")
    @commands.is_owner()
    async def logs(self, ctx, file: bool = False):
        """Get the logs"""
        if file:
            return await ctx.respond(file=File(Owner.LOGS_FILE_PATH), ephemeral=True)
        else:
            with open(Owner.LOGS_FILE_PATH, "r") as f:
                text = f.read()
                return await ctx.respond(
                    f"```{text[len(text)-1994:]}```", ephemeral=True
                )

    @owner.command(name="clear_logs")
    @commands.is_owner()
    async def clear_logs(self, ctx):
        """Clear the logs"""
        with open(Owner.LOGS_FILE_PATH, "w") as f:
            f.write("")
        await ctx.respond("Logs cleared", ephemeral=True)

    @owner.command(name="test_welcome_card")
    @commands.is_owner()
    async def test_welcome_card(self, ctx):
        card = WelcomeCard.create_card(ctx.author, ctx.author.guild)
        try:
            await ctx.channel.send(
                file=File(fp=card, filename=f"welcome_{ctx.author.name}.png")
            )
        except commands.MissingPermissions:
            return await ctx.respond(
                "I don't have permission to send images in this channel",
                ephemeral=True,
            )
        return await ctx.respond("Done!", ephemeral=True)
