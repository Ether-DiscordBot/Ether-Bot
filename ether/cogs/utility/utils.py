from random import random, choice
import re
import requests
from typing import List, Optional

from discord import ApplicationContext, Embed, Option, OptionChoice
from discord.commands import SlashCommandGroup, slash_command
from discord.ext import commands

from ether.core.utils import EtherEmbeds

URBAN_PATTERN = r"\[(.*?)]"


class Utils(commands.Cog, name="utils"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "🔧 Utility"

        help_embed = Embed(
            description="Get more information about these [commands](https://www.youtube.com/watch?v=dQw4w9WgXcQ)."
        )
        cogs = []
        for _name, cog in self.client.cogs.items():
           cogs.append(f"`{cog.fancy_name}`")
        
        help_embed.add_field(name="List of all cogs", value=f"{', '.join(cogs)}")
        
        self.help_embed = help_embed

    utils = SlashCommandGroup("utils", "Utils commands!")

    @slash_command(name="help")
    async def help(self, ctx: ApplicationContext, category: Option(str, "Pick a category", required=False, choices=[OptionChoice(name="Admin", value="admin"), # TODO Make that more properly
                                                                                                     OptionChoice(name="DnD", value="dnd"),
                                                                                                     OptionChoice(name="Fun", value="fun"),
                                                                                                     OptionChoice(name="Games", value="games"),
                                                                                                     OptionChoice(name="Image", value="image"),
                                                                                                     OptionChoice(name="Information", value="information"),
                                                                                                     OptionChoice(name="Leveling", value="levels"),
                                                                                                     OptionChoice(name="Music", value="music"),
                                                                                                     OptionChoice(name="Nasa", value="nasa"),
                                                                                                     OptionChoice(name="Reddit", value="reddit"),
                                                                                                     OptionChoice(name="Steam", value="steam")])=None) -> None:
        if not category:
            return await ctx.respond(embed=self.help_embed, ephemeral=True)

        embed = Embed(description="Check the list of all [commands](https://www.youtube.com/watch?v=dQw4w9WgXcQ).\n\n", title=category)
        for cmd in self.client.get_cog(category).walk_commands():
            embed.description += f"`\{cmd}`\n"
        
        return await ctx.respond(embed=embed, ephemeral=True)

    @slash_command()
    async def ping(self, ctx: ApplicationContext) -> None:
        embed = Embed(
            title=":ping_pong: Pong !",
            description=f"Bot latency: `{round(self.client.latency * 1000)}ms`",
        )

        await ctx.respond(embed=embed)

    @utils.command(name="flipcoin")
    async def flip_coin(self, ctx: ApplicationContext) -> None:
        result = "Heads" if round(random()) else "Tails"
        await ctx.respond(result)

    @utils.command(name="choose")
    async def choose(
        self,
        ctx: ApplicationContext,
        first: str,
        second: str,
        third: Optional[str] = None,
        fourth: Optional[str] = None,
        fifth: Optional[str] = None,
        sisth: Optional[str] = None,
        seventh: Optional[str] = None,
        eighth: Optional[str] = None,
        ninth: Optional[str] = None,
        tenth: Optional[str] = None,
    ):
        items = [
            first,
            second,
            third,
            fourth,
            fifth,
            sisth,
            seventh,
            eighth,
            ninth,
            tenth,
        ]
        list = [i for i in items if i]
        return await ctx.respond(choice(list))

    @utils.command(name="urban")
    async def urban(self, ctx: ApplicationContext, term: str):
        r = requests.get(f"https://api.urbandictionary.com/v0/define?term={term}")
        res = r.json()

        if len(res["list"]) > 0:
            link = f"https://www.urbandictionary.com/define.php?term={term}"

            embed = Embed(title=f'Definition of "{term}":', url=link)
            embed.set_footer(
                text="Powered by Urban Dictionary",
                icon_url="https://img.utdstc.com/icon/4af/833/4af833b6befdd4c69d7ebac403bfa087159601c9c129e4686b8b664e49a7f349",
            )

            definition = res["list"][0]["definition"]
            if len(definition) > 1024:
                definition = f"\t{definition[:1023]}..."

            linked_definition = ""
            substring = re.finditer(URBAN_PATTERN, definition)
            splitted = re.split(URBAN_PATTERN, definition)

            i = 0
            for s in substring:
                b_before = splitted[i]
                before = definition[s.span()[0] : s.span()[1]]

                link = f"https://www.urbandictionary.com/define.php?term={splitted[i+1]}".replace(
                    " ", "%20"
                )
                i += 2

                linked_definition += b_before + before + f"({link})"

            embed.description = linked_definition

            await ctx.respond(embed=embed)
        else:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    f'Could not find any definition of **"{term}"**!'
                ),
                delete_after=5,
            )
