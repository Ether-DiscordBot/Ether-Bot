import re
import operator
from random import choice, random, randint
from typing import Optional

import requests
from discord import ApplicationContext, Embed, Option
from discord.commands import SlashCommandGroup, slash_command
from discord.ext import commands
from howlongtobeatpy import HowLongToBeat

from ether.core.i18n import _
from ether.core.utils import EtherEmbeds
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji

URBAN_PATTERN = r"\[(.*?)]"
ops = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


class Utils(commands.Cog, name="utils"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.UTILITY

    utils = SlashCommandGroup("utils", "Utility commands!")

    @slash_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vote(self, ctx: ApplicationContext) -> None:
        """Get the link to vote for the bot"""

        await ctx.respond(
            embed=Embed(
                title="Thank you for supporting us ❤️!",
                description=_(
                    "Click [here](https://top.gg/bot/985100792270819389/vote) to vote for me!"
                ),
            )
        )

    @slash_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def ping(self, ctx: ApplicationContext) -> None:
        """Pong!"""

        await ctx.respond(
            embed=Embed(
                title=":ping_pong: Pong !",
                description=f"Bot latency: `{round(self.client.latency * 1000)}ms`",
            )
        )

    @utils.command(name="flipcoin")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def flip_coin(self, ctx: ApplicationContext) -> None:
        """Flip a coin"""
        result = _("Heads") if round(random()) else _("Tails")
        await ctx.respond(result)

    @utils.command(name="choose")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
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
        """Choose between multiple options"""
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

    @utils.command(name="roll")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def roll(
        self,
        ctx: ApplicationContext,
        dice: Option(str, "Dices to roll. (syntax: `1d6, 2d20+2`)", required=True),
    ):
        """Roll a dice"""

        def eval_binary_expr(op1, oper, op2):
            op1, op2 = int(op1), int(op2)
            return ops[oper](op1, op2)

        def _roll(match):
            a, b = match.group(1).split("d")
            return str(randint(int(a), int(a) * int(b)))

        try:
            results = [r.lstrip() for r in re.sub("(\d+d\d+)", _roll, dice).split(",")]
            result = [
                eval_binary_expr(*re.findall(r"(?:\d+)|(?:[\+\-\*\/])", r))
                if not r.isdigit()
                else r
                for r in results
            ]

        except Exception:
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    "An error occured, please check the syntax of your dices."
                ),
                ephemeral=True,
                delete_after=5,
            )

        result = "\n".join(
            f"║ {str(t).lstrip().ljust(10)}║ {str(r).lstrip().ljust(5)}║"
            for t, r in zip(dice.split(","), result)
        )
        await ctx.respond(
            f"```\n╔═══════════╦══════╗\n║ Dice      ║ Sum  ║\n╟───────────╫──────╢\n{result}\n╚═══════════╩══════╝```"
        )

    @utils.command(name="urban")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def urban(self, ctx: ApplicationContext, term: str):
        """Search for a term on Urban Dictionary"""
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

    @utils.command(name="howlongtobeat")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def howlongtobeat(self, ctx: ApplicationContext, game: str):
        """Get the time to beat a game"""
        results_list = await HowLongToBeat().async_search(game_name=game)
        if results_list is not None and len(results_list) > 0:
            data = max(results_list, key=lambda element: element.similarity)
        else:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, we could not find your game."),
                ephemeral=True,
            )

        embed = Embed(title=data.game_name, url=data.game_web_link)
        embed.add_field(
            name=data.gameplay_main_label,
            value=f"{data.gameplay_main} {data.gameplay_main_unit}",
        )
        embed.add_field(
            name=data.gameplay_main_extra_label,
            value=f"{data.gameplay_main_extra} {data.gameplay_main_extra_unit}",
        )
        embed.add_field(
            name=data.gameplay_completionist_label,
            value=f"{data.gameplay_completionist} {data.gameplay_completionist_unit}",
        )

        embed.set_thumbnail(url=f"https://howlongtobeat.com{data.game_image_url}")
        embed.set_footer(
            text="Powered by howlongtobeat.com",
            icon_url="https://pbs.twimg.com/profile_images/433503450404368384/tdnd53zT_400x400.png",
        )

        await ctx.respond(embed=embed)
