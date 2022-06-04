from random import random
import time

from discord import Embed, Interaction
from discord.commands import SlashCommandGroup, slash_command
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Misc"
        
        help_embed = Embed(
            description="Get more information about these [commands](https://www.youtube.com/watch?v=dQw4w9WgXcQ)."
        )
        for _name, cog in self.client.cogs.items():
            field = {"name": cog.fancy_name, "value": []}
            for cmd in cog.get_commands():
                field["value"].append(cmd.name)
            help_embed.add_field(
                name=field["name"], value=", ".join(field["value"]), inline=False
        )
        
        self.help_embed = help_embed

    misc = SlashCommandGroup("misc", "Miscelanious commands!")
    
    @slash_command(name="help", guild_ids=[697735468875513876])
    async def help(self, interaction: Interaction) -> None:
        await interaction.response.send_message(embed=self.help_embed)

    @slash_command()
    async def ping(self, interaction: Interaction) -> None:
        embed = Embed(title=":ping_pong: Pong !", description=f"Bot latency: `{round(self.client.latency * 1000)}ms`")
        
        await interaction.response.send_message(embed=embed)

    @misc.command(name='flipcoin')
    async def flip_coin(self, interaction: Interaction) -> None:
        result = "Heads" if round(random()) else "Tails"
        await interaction.response.send_message(result)
