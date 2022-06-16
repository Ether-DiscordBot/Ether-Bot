from random import random, choice
from typing import List, Optional
from discord import ApplicationContext, Embed
from discord.commands import SlashCommandGroup, slash_command
from discord.ext import commands
from typer import Option

class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Utility"
        
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

    utils = SlashCommandGroup("utils", "Utils commands!")
    
    @slash_command(name="help", guild_ids=[697735468875513876])
    async def help(self, ctx: ApplicationContext) -> None:
        await ctx.respond(embed=self.help_embed)

    @slash_command()
    async def ping(self, ctx: ApplicationContext) -> None:
        embed = Embed(title=":ping_pong: Pong !", description=f"Bot latency: `{round(self.client.latency * 1000)}ms`")
        
        await ctx.respond(embed=embed)

    @utils.command(name='flipcoin')
    async def flip_coin(self, ctx: ApplicationContext) -> None:
        result = "Heads" if round(random()) else "Tails"
        await ctx.respond(result)
        
    @utils.command(name='choose')
    async def choose(self, ctx: ApplicationContext,
                     first: str,
                     second: str,
                     third: Optional[str] = None,
                     fourth: Optional[str] = None,
                     fifth: Optional[str] = None,
                     sisth: Optional[str] = None,
                     seventh: Optional[str] = None,
                     eighth: Optional[str] = None,
                     ninth: Optional[str] = None,
                     tenth: Optional[str] = None
                     ):
        items = [first, second, third, fourth, fifth, sisth, seventh, eighth, ninth, tenth]
        list = [i for i in items if i]
        return await ctx.respond(choice(list))
