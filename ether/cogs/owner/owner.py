import os
from discord import SlashCommandGroup, File
from discord.ext import commands


class Owner(commands.Cog):
    LOGS_FILE_PATH = os.path.abspath("logs.log")

    def __init__(self, client):
        self.client = client

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
