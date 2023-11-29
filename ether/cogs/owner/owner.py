import os

import discord
import wavelink
from discord import File, app_commands
from discord.ext import commands

from ether.cogs.event.welcomecard import WelcomeCard
from ether.core.constants import Colors, Emoji
from ether.core.embed import Embed


@app_commands.guilds(1027277588399403070, 697735468875513876)
class Owner(commands.GroupCog, name="owner"):
    LOGS_FILE_PATH = os.path.abspath("logs.log")

    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.OWNER

    @app_commands.command(name="logs")
    @commands.is_owner()
    async def logs(self, interaction: discord.Interaction, file: bool = False):
        """Get the logs"""
        if file:
            return await interaction.response.send_message(
                file=File(Owner.LOGS_FILE_PATH), ephemeral=True
            )
        with open(Owner.LOGS_FILE_PATH, "r") as f:
            text = f.read()
            return await interaction.response.send_message(
                f"```{text[len(text)-1994:]}```", ephemeral=True
            )

    @app_commands.command(name="clear_logs")
    @commands.is_owner()
    async def clear_logs(self, interaction: discord.Interaction):
        """Clear the logs"""
        with open(Owner.LOGS_FILE_PATH, "w") as f:
            f.write("")
        await interaction.response.send_message("Logs cleared", ephemeral=True)

    async def test_welcome_card(self, interaction: discord.Interaction):
        card = WelcomeCard.create_card(
            interaction.user, interaction.user.guild
        )
        try:
            await interaction.channel.send(
                file=File(
                    fp=card, filename=f"welcome_{interaction.user.name}.png"
                )
            )
        except commands.MissingPermissions:
            return await interaction.response.send_message(
                "I don't have permission to send images in this channel",
                ephemeral=True,
            )
        return await interaction.response.send_message("Done!", ephemeral=True)

    @app_commands.command(name="server_count")
    @commands.is_owner()
    async def server_count(self, interaction: discord.Interaction):
        """Get the server count"""
        return await interaction.response.send_message(
            embed=Embed(description=f"Server count: `{len(self.client.guilds)}`"),
            ephemeral=True,
        )

    @app_commands.command(name="lavalinkinfo")
    @commands.is_owner()
    async def lavalink_info(self, interaction: discord.Interaction):
        """Show lavalink info"""
        embed = Embed(title=f"**Wavelink:** `{wavelink.__version__}`", color=Colors.DEFAULT)

        embed.add_field(
            name="Server",
            value=f"Server Nodes: `{len(wavelink.Pool.nodes)}`\n"
            f"Voice Client Connected: `{len(self.client.voice_clients)}`\n",
            inline=False,
        )

        nodes = [
            f"`{identifier}`({len(node.players)})"
            for identifier, node in wavelink.Pool.nodes.items()
        ]
        embed.add_field(name="Nodes", value=f"{', '.join(nodes)}", inline=False)
        await interaction.response.send_message(embed=embed)
