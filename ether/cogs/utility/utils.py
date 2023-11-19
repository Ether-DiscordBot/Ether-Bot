import datetime
import operator
import re
from random import choice, randint, random
from typing import Optional

import discord
import pytz
import requests
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from howlongtobeatpy import HowLongToBeat

from ether.cogs.utility.uptime_cards import UptimeCards
from ether.core.constants import Emoji
from ether.core.embed import Embed, ErrorEmbed, SuccessEmbed
from ether.core.i18n import _
from ether.core.logging import log

URBAN_PATTERN = r"\[(.*?)]"
ops = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


def hltb_time(time: float) -> str:
    time = str(time).split(".")
    time[1] = int(time[1])
    time[1] = "" if time[1] < 34 or time[1] > 67 else "½"

    return f"{''.join(time)} Hours"

print(__name__)


class Utils(commands.GroupCog, name="utils"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.UTILITY

        self.monitors_card: discord.File | None = None
        self.monitor_card_builder.start()

    @tasks.loop(minutes=30.0)
    async def monitor_card_builder(self):
        log.debug("Building monitor cards...")
        self.monitors_card = UptimeCards().card

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def vote(self, interaction: discord.Interaction) -> None:
        """Get the link to vote for the bot"""

        await interaction.response.send_message(
            embed=Embed(
                title="Thank you for supporting us ❤️!",
                description=_(
                    "Click [here](https://top.gg/bot/985100792270819389/vote) to vote for me!"
                ),
            )
        )

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def changelog(self, interaction: discord.Interaction) -> None:
        """Get the changelog"""

        changelog = "# Latest changes\n\n"

        with open("CHANGELOG.md", "r") as f:
            lines = f.readlines()

            content = "".join(lines)
            content = content.split("##")[:5]

            changelog += "##".join(content)

        await interaction.response.send_message(f"```md\n{changelog}\n```")

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def ping(self, interaction: discord.Interaction) -> None:
        """Pong!"""

        embed = SuccessEmbed(
            title=":ping_pong:" + _("Pong!"),
            description=_("Bot latency: `{x}ms`", x=round(self.client.latency * 1000)),
        )

        await interaction.response.send_message(
            embed=SuccessEmbed(
                title=":ping_pong:" + _("Pong!"),
                description=_(
                    "Bot latency: `{x}ms`", x=round(self.client.latency * 1000)
                ),
            )
        )

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def status(self, interaction: discord.Interaction) -> None:
        """Show the status of Ether"""

        await interaction.response.send_message(
            embed=Embed(
                title="🟢 Ether Status",
                description="Here is the [Ether's status page](https://stats.uptimerobot.com/yxDgrt60O3).",
            )
        )

    @app_commands.command(name="flipcoin")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def flip_coin(self, interaction: discord.Interaction) -> None:
        """Flip a coin"""
        result = _("Heads") if round(random()) else _("Tails")
        await interaction.response.send_message(result)

    @app_commands.command(name="choose")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def choose(
        self,
        interaction: discord.Interaction,
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
        return await interaction.response.send_message(choice(list))

    @commands.command(name="roll")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(dice="Dices to roll. (syntax: `1d6, 2d20+2`)")
    async def roll(
        self,
        interaction: discord.Interaction,
        dice: str,
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
            return await interaction.response.send_message(
                embed=ErrorEmbed(
                    _("An error occurred, please check the syntax of your dices.")
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

        await interaction.response.send_message(
            f"```\n╔══════{'═' * max(6, most_larger_dice_str-4)}╦═════════{'═' * max(0, most_details_dice_str-7)}╦═════{'═' * max(1, most_larger_result_str-5)}╗"
            f"\n║ Dice {' ' * max(6, most_larger_dice_str-4)}║ Details {' ' * max(0, most_details_dice_str-7)}║ Sum {' ' * max(1, most_larger_result_str-5)}║"
            f"\n╟──────{'─' * max(6, most_larger_dice_str-4)}╫─────────{'─' * max(0, most_details_dice_str-7)}╫─────{'─' * max(1, most_larger_result_str-5)}╢\n{result}"
            f"\n╚══════{'═' * max(6, most_larger_dice_str-4)}╩═════════{'═' * max(0, most_details_dice_str-7)}╩═════{'═' * max(1, most_larger_result_str-5)}╝```"
        )

    @app_commands.command(name="urban")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def urban(self, interaction: discord.Interaction, term: str):
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
            split = re.split(URBAN_PATTERN, definition)

            i = 0
            for s in substring:
                b_before = split[i]
                before = definition[s.span()[0] : s.span()[1]]

                link = f"https://www.urbandictionary.com/define.php?term={split[i+1]}".replace(
                    " ", "%20"
                )
                i += 2

                linked_definition += b_before + before + f"({link})"

            embed.description = linked_definition

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                embed=ErrorEmbed('Could not find any definition of **"{term}"**!'),
                delete_after=5,
            )

    @app_commands.command(name="howlongtobeat")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def howlongtobeat(self, interaction: discord.Interaction, game: str):
        """Get the time to beat a game"""
        results_list = await HowLongToBeat().async_search(game_name=game)
        if results_list and len(results_list) > 0:
            data = max(results_list, key=lambda element: element.similarity)
        else:
            return await interaction.response.send_message(
                embed=ErrorEmbed("Sorry, we could not find your game."),
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

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rocket_launches")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(
        timezone=[
            Choice(name="UTC-7", value="ETC/GMT-7"),
            Choice(name="UTC-6", value="ETC/GMT-6"),
            Choice(name="UTC-5", value="ETC/GMT-5"),
            Choice(name="UTC-4", value="ETC/GMT-4"),
            Choice(name="UTC-3", value="ETC/GMT-3"),
            Choice(name="UTC", value="ETC/UTC"),
            Choice(name="UTC+1", value="ETC/GMT+1"),
            Choice(name="UTC+2", value="ETC/GMT+2"),
            Choice(name="UTC+3", value="ETC/GMT+3"),
            Choice(name="UTC+4", value="ETC/GMT+4"),
            Choice(name="UTC+5", value="ETC/GMT+5"),
            Choice(name="UTC+8", value="ETC/GMT+8"),
            Choice(name="UTC+9", value="ETC/GMT+9"),
            Choice(name="UTC+10", value="ETC/GMT+10"),
            Choice(name="UTC+12", value="ETC/GMT+12"),
        ]
    )
    async def rocket_launches(
        self,
        interaction: discord.Interaction,
        timezone: Choice[str],
    ):
        """Get the next rocket launches"""
        timezone = pytz.timezone(timezone)

        r = requests.get("https://fdo.rocketlaunch.live/json/launches/next/5")
        res = r.json()

        embed = Embed(
            title="🚀 Next 5 rocket launches",
            description="*(date format: dd/mm/YYYY, HH:MM)*",
        )
        embed.set_footer(
            text="Powered by rocketlaunch.live",
            icon_url="https://rocketlaunch.live/favicon16.png",
        )

        for launch in res["result"]:
            date = datetime.datetime.fromtimestamp(
                int(launch["sort_date"]), tz=timezone
            ).strftime("%d/%m/%Y, %H:%M")
            index = res["result"].index(launch) + 1

            field_value = "\n".join(
                [
                    launch["quicktext"].split("- https")[0],
                    f"*📆 {date}*",
                    f"*📍 at {launch['pad']['location']['name']}*",
                ]
            )

            embed.add_field(
                name=f"[{index}] **{launch['name']}**",
                value=field_value,
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="uptime")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def uptime(self, interaction: discord.Interaction):
        if not self.monitors_card:
            return await interaction.response.send_message(
                embed=ErrorEmbed(description="Sorry, uptime cards are not available yet, retry later.")
            )

        await interaction.response.send_message(
            file=self.monitors_card
        )
