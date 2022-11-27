from random import choice, randint, seed
from typing import Optional
from requests import get, request
import os

from discord import (
    ApplicationCommand,
    Embed,
    ApplicationContext,
    Member,
    Option,
    OptionChoice,
    SlashCommandGroup,
)
from discord.ext import commands
from howlongtobeatpy import HowLongToBeat

from ether.core.i18n import _
from ether.core.utils import EtherEmbeds, NerglishTranslator
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


class Fun(commands.Cog, name="fun"):
    SUPPORTED_EMBED_FORMAT = ("jpg", "jpeg", "JPG", "JPEG", "png", "PNG", "gif", "gifv")
    HEIGHT_BALL_ANSWERS = [
        [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may reply on it.",
            "As I see it, yes.",
            "Most likely",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
        ],
        [
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
        ],
        [
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ],
    ]

    def __init__(self, client):
        self.help_icon = Emoji.FUN
        self.client = client

        self.giphy_api_key = os.getenv("GIPHY_API_KEY")

    fun = SlashCommandGroup("fun", "Fun commands!")

    @fun.command()
    @locale_doc
    async def gif(self, ctx: ApplicationContext, *, query):
        """Search a gif on giphy"""
        r = get(
            f"https://api.giphy.com/v1/gifs/random?tag={query}&api_key={self.giphy_api_key}"
        )

        r = r.json()
        if not r["data"]:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    "Sorry, I could not find any gifs with this query.", delete_after=5
                )
            )
            return
        gif_url = r["data"]["url"]

        await ctx.respond(gif_url)

    @fun.command()
    async def sticker(self, ctx: ApplicationContext, *, query):
        """Search a sticker on giphy"""
        r = get(
            f"https://api.giphy.com/v1/stickers/random?tag={query}&api_key={self.giphy_api_key}"
        )

        r = r.json()
        if not r["data"]:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    "Sorry, I could not find any gifs with this query.", delete_after=5
                )
            )
            return
        sticker_url = r["data"]["images"]["original"]["url"]

        await ctx.respond(sticker_url)

    @fun.command(name="8-ball")
    async def height_ball(self, ctx: ApplicationContext, question: str):
        """Ask the magic 8-ball a question!"""

        await ctx.respond(f"🎱 {choice(choice(self.HEIGHT_BALL_ANSWERS))}")

    @fun.command(name="say")
    async def say(
        self,
        ctx: ApplicationContext,
        message: str,
        hide: Option(bool, "Hide ?", default=False),
    ):
        """Make the bot say something"""

        if hide:
            await ctx.respond(
                "👌 Done! (only you can see this message)",
                ephemeral=True,
                delete_after=5,
            )
            await ctx.channel.send(message)
            return

        await ctx.respond(message)

    @fun.command(name="howgay")
    async def howgay(self, ctx: ApplicationContext, user: Optional[Member] = None):
        """The bot guesses how gay your are"""

        user = ctx.author if not user else user

        seed(user.id / 268)
        gaymeter = randint(0, 100)

        if user == ctx.author:
            return await ctx.respond(f"You are gay at `{gaymeter}%` !")
        await ctx.respond(f"{user.mention} is gay at `{gaymeter}%` !")

    @fun.command(name="attractive")
    async def pretty(self, ctx: ApplicationContext, user: Optional[Member] = None):
        """The bot tells you how attractive you are"""

        user = ctx.author if not user else user

        seed(user.id / 294)
        attractivemeter = randint(0, 100)

        if user == ctx.author:
            return await ctx.respond(f"You are `{attractivemeter}%` attractive !")
        await ctx.respond(f"{user.mention} is `{attractivemeter}%` attractive !")

    @fun.command(name="hot")
    async def hot(self, ctx: ApplicationContext, user: Optional[Member] = None):
        """The bot guesses how hot you are"""

        user = ctx.author if not user else user

        seed(user.id / 15)
        hotmeter = randint(0, 100)

        if user == ctx.author:
            return await ctx.respond(f"You are `{hotmeter}%` hot!")
        await ctx.respond(f"{user.mention} is `{hotmeter}%` hot!")

    @fun.command(name="horoscope")
    async def horoscope(
        self,
        ctx: ApplicationContext,
        sign: Option(
            str,
            "choose an astrological sign",
            required=True,
            choices=[
                OptionChoice("♈ Aries", value="aries"),
                OptionChoice("♉ Taurus", value="taurus"),
                OptionChoice("♊ Gemini", value="gemini"),
                OptionChoice("♋ Cancer", value="cancer"),
                OptionChoice("♌ Leo", value="leo"),
                OptionChoice("♍ Virgo", value="virgo"),
                OptionChoice("♎ Libra", value="libra"),
                OptionChoice("♏ Scorpius", value="scorpio"),
                OptionChoice("♐ Sagittarius", value="sagittarius"),
                OptionChoice("♑ Capricorn", value="capricorn"),
                OptionChoice("♒ Aquarius", value="aquarius"),
                OptionChoice("♓ Pisces", value="pisces"),
            ],
        ),
    ):
        """Get your daily horoscope"""
        url = f"https://ohmanda.com/api/horoscope/{sign}"

        response = request("POST", url)
        r = response.json()

        embed = Embed(
            title=f":{sign.lower()}: Horoscope", description=f"{r['horoscope']}\n\n"
        )

        await ctx.respond(embed=embed)

    @fun.command(name="nerglish")
    async def nerglish(self, ctx: ApplicationCommand, text: str):
        """Translate text to nerglish"""
        translated = NerglishTranslator.translate(text)
        await ctx.respond(translated)

    @fun.command(name="howlongtobeat")
    async def howlongtobeat(self, ctx: ApplicationCommand, game: str):
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
