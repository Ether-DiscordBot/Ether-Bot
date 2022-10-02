from random import random, choice
import re
from threading import local
import requests
from typing import List, Optional

from discord import ApplicationContext, Embed, Option, OptionChoice
from discord.commands import SlashCommandGroup, slash_command
from discord.ext import commands

from ether.core.utils import EtherEmbeds
from ether.core.i18n import locale_doc, _

URBAN_PATTERN = r"\[(.*?)]"


class Utils(commands.Cog, name="utils"):
    def __init__(self, client):
        self.client = client

    utils = SlashCommandGroup("utils", "Utils commands!")

    @slash_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def ping(self, ctx: ApplicationContext) -> None:
        """Pong!"""

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
