import datetime
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
from ether.core.constants import Emoji

URBAN_PATTERN = r"\[(.*?)]"
ops = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


def hltb_time(time: float) -> str:
    time = str(time).split(".")
    time[1] = int(time[1])
    time[1] = "" if time[1] < 34 or time[1] > 67 else "½"

    return f"{''.join(time)} Hours"


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
    async def ping(self, ctx: ApplicationContext) -> None:
        """Pong!"""

        await ctx.respond(
            embed=Embed(
                title=":ping_pong:" + _("Pong!"),
                description=_(
                    "Bot latency: `{x}ms`", x=round(self.client.latency * 1000)
                ),
            )
        )

    @utils.command(name="flipcoin")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def flip_coin(self, ctx: ApplicationContext) -> None:
        """Flip a coin"""
        result = _("Heads") if round(random()) else _("Tails")
        await ctx.respond(result)

    @utils.command(name="choose")
    @commands.cooldown(1, 5, commands.BucketType.user)
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

    @commands.slash_command(name="roll")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roll(
        self,
        ctx: ApplicationContext,
        dice: Option(str, "Dices to roll. (syntax: `1d6, 2d20+2`)", required=True),
    ):
        """Roll a dice"""

        def eval_binary_expr(r):
            expr = [*re.findall(r"(?:\d+)|(?:[\+\-\*\/])", r)]

            while len(expr) > 1:
                if len(expr) >= 3:
                    op1, oper, op2, *expr = expr
                else:
                    raise ValueError("Invalid expression")

                expr = [ops[oper](int(op1), int(op2))] + expr

            return expr[0]

        def _roll(match):
            a, b = match.group(1).split("d")
            return str(sum([randint(1, int(b)) for _ in range(int(a))]))

        try:
            details = [r.lstrip() for r in re.sub("(\d+d\d+)", _roll, dice).split(",")]
            result = [eval_binary_expr(r) if not r.isdigit() else r for r in details]

        except ValueError:
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    _("An error occured, please check the syntax of your dices.")
                ),
                ephemeral=True,
                delete_after=5,
            )

        most_larger_dice_str = len(max(dice.split(","), key=len))
        most_details_dice_str = len(max(details, key=len))
        most_larger_result_str = len(max([str(r) for r in result], key=len))

        result = "\n".join(
            f"║ {str(t).lstrip().ljust(max(10, most_larger_dice_str))} ║ {str(d).lstrip().ljust(max(7, most_details_dice_str))} ║ {str(r).lstrip().ljust(max(4, most_larger_result_str))} ║"
            for t, d, r in zip(dice.split(","), details, result)
        )

        await ctx.respond(
            f"```\n╔══════{'═' * max(6, most_larger_dice_str-4)}╦═════════{'═' * max(0, most_details_dice_str-7)}╦═════{'═' * max(1, most_larger_result_str-5)}╗"
            f"\n║ Dice {' ' * max(6, most_larger_dice_str-4)}║ Details {' ' * max(0, most_details_dice_str-7)}║ Sum {' ' * max(1, most_larger_result_str-5)}║"
            f"\n╟──────{'─' * max(6, most_larger_dice_str-4)}╫─────────{'─' * max(0, most_details_dice_str-7)}╫─────{'─' * max(1, most_larger_result_str-5)}╢\n{result}"
            f"\n╚══════{'═' * max(6, most_larger_dice_str-4)}╩═════════{'═' * max(0, most_details_dice_str-7)}╩═════{'═' * max(1, most_larger_result_str-5)}╝```"
        )

    @utils.command(name="urban")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
                    'Could not find any definition of **"{term}"**!'
                ),
                delete_after=5,
            )

    @utils.command(name="howlongtobeat")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def howlongtobeat(self, ctx: ApplicationContext, game: str):
        """Get the time to beat a game"""
        results_list = await HowLongToBeat().async_search(game_name=game)
        if results_list and len(results_list) > 0:
            data = max(results_list, key=lambda element: element.similarity)
        else:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, we could not find your game."),
                ephemeral=True,
            )

        embed = Embed(title=data.game_name, url=data.game_web_link)
        if data.main_story:
            embed.add_field(
                name="Main Story",
                value=hltb_time(data.main_story),
            )
        if data.main_extra:
            embed.add_field(
                name="Main Extra",
                value=hltb_time(data.main_extra),
            )
        if data.completionist:
            embed.add_field(
                name="Completionist",
                value=hltb_time(data.completionist),
            )
        if data.all_styles:
            embed.add_field(
                name="All styles",
                value=hltb_time(data.all_styles),
            )

        embed.set_thumbnail(url=data.game_image_url)
        embed.set_footer(
            text="Powered by howlongtobeat.com",
            icon_url="https://pbs.twimg.com/profile_images/433503450404368384/tdnd53zT_400x400.png",
        )

        await ctx.respond(embed=embed)

    @utils.command(name="rocket_launches")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rocket_launches(self, ctx: ApplicationContext):
        """Get the next rocket launches"""
        r = requests.get("https://fdo.rocketlaunch.live/json/launches/next/5")
        res = r.json()

        embed = Embed(title="Next rocket launches")
        embed.set_footer(
            text="Powered by rocketlaunch.live",
            icon_url="https://rocketlaunch.live/favicon16.png",
        )

        for launch in res["result"]:
            index = res["result"].index(launch) + 1

            field_value = "\n".join(
                [
                    launch["launch_description"],
                    f"**Pad:** {launch['pad']['name']} at **{launch['pad']['location']['name']}**",
                ]
            )

            embed.add_field(
                name=f"[{index}] **{launch['name']}**",
                value=field_value,
                inline=False,
            )

        await ctx.respond(embed=embed)
