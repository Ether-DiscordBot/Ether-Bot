from random import choice, randint, seed
from typing import Optional
from requests import get, request
import os
import urllib.parse

from discord import (
    ApplicationContext,
    Embed,
    ApplicationContext,
    Member,
    Option,
    OptionChoice,
    SlashCommandGroup,
)
from discord.ext import commands

from ether.core.i18n import _
from ether.core.utils import EtherEmbeds, NerglishTranslator
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

    @fun.command(name="gif")
    @commands.cooldown(1, 5, commands.BucketType.user)
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

    @fun.command(name="sticker")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def height_ball(self, ctx: ApplicationContext, question: str):
        """Ask the magic 8-ball a question!"""

        await ctx.respond(f"🎱 {choice(choice(self.HEIGHT_BALL_ANSWERS))}")

    @fun.command(name="say")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def howgay(self, ctx: ApplicationContext, user: Optional[Member] = None):
        """The bot guesses how gay your are"""

        user = user or ctx.author

        seed(user.id / 268)
        gaymeter = randint(0, 100)

        if user == ctx.author:
            return await ctx.respond(f"You are gay at `{gaymeter}%` !")
        await ctx.respond(f"{user.mention} is gay at `{gaymeter}%` !")

    @fun.command(name="howattractive")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def howattractive(
        self, ctx: ApplicationContext, user: Optional[Member] = None
    ):
        """The bot tells you how attractive you are"""

        user = user or ctx.author

        seed(user.id / 294)
        attractivemeter = randint(0, 100)

        if user == ctx.author:
            return await ctx.respond(f"You are `{attractivemeter}%` attractive!")
        await ctx.respond(f"{user.mention} is `{attractivemeter}%` attractive!")

    @fun.command(name="howhot")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def howhot(self, ctx: ApplicationContext, user: Optional[Member] = None):
        """The bot guesses how hot you are"""

        user = user or ctx.author

        seed(user.id / 15)
        hotmeter = randint(0, 100)

        if user == ctx.author:
            return await ctx.respond(f"You are `{hotmeter}%` hot!")
        await ctx.respond(f"{user.mention} is `{hotmeter}%` hot!")

    @fun.command(name="horoscope")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nerglish(self, ctx: ApplicationContext, text: str):
        """Translate text to nerglish"""
        translated = NerglishTranslator.translate(text)
        await ctx.respond(translated)

    @fun.command(name="lmgtfy")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lmgtfy(self, ctx: ApplicationContext, text: str):
        """Let me google that for you"""
        await ctx.respond(
            f"https://letmegooglethat.com/?q={urllib.parse.quote_plus(text)}"
        )
