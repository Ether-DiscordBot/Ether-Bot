import urllib.parse
from random import choice, randint, seed
from typing import Optional

import discord
from discord import Member, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from requests import request

from ether.core.constants import Emoji
from ether.core.embed import Embed
from ether.core.i18n import _
from ether.core.utils import NerglishTranslator


class Fun(commands.GroupCog, name="fun"):
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

    @app_commands.command(name="8-ball")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def height_ball(self, interaction: discord.Interaction, question: str):
        """Ask the magic 8-ball a question!"""

        await interaction.response.send_message(
            f"🎱 {choice(choice(self.HEIGHT_BALL_ANSWERS))}"
        )

    @app_commands.command(name="say")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        hide: bool,
    ):
        """Make the bot say something"""

        if hide:
            await interaction.channel.send(message)
            await interaction.response.send_message(
                "👌 Done!",
                ephemeral=True,
                delete_after=5,
            )
            return

        await interaction.response.send_message(message)

    @app_commands.command(name="howgay")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def howgay(
        self, interaction: discord.Interaction, user: Optional[Member] = None
    ):
        """The bot guesses how gay your are"""

        user = interaction.user if not user else user

        seed(user.id / 1782)
        gaymeter = randint(0, 100)

        if user == interaction.user:
            return await interaction.response.send_message(
                f"You are gay at `{gaymeter}%` !"
            )
        await interaction.response.send_message(
            f"{user.mention} is gay at `{gaymeter}%` !"
        )

    @app_commands.command(name="howattractive")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def howattractive(
        self, interaction: discord.Interaction, user: Optional[Member] = None
    ):
        """The bot tells you how attractive you are"""

        user = interaction.user if not user else user

        seed(user.id / 294)
        attractivemeter = randint(0, 100)

        if user == interaction.user:
            return await interaction.response.send_message(
                f"You are `{attractivemeter}%` attractive!"
            )
        await interaction.response.send_message(
            f"{user.mention} is `{attractivemeter}%` attractive!"
        )

    @app_commands.command(name="howhot")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def howhot(
        self, interaction: discord.Interaction, user: Optional[Member] = None
    ):
        """The bot guesses how hot you are"""

        user = interaction.user if not user else user

        seed(user.id / 15)
        hotmeter = randint(0, 100)

        if user == interaction.user:
            return await interaction.response.send_message(
                f"You are `{hotmeter}%` hot!"
            )
        await interaction.response.send_message(f"{user.mention} is `{hotmeter}%` hot!")

    @app_commands.command(name="lovecalc")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def howhot(
        self,
        interaction: discord.Interaction,
        user1: Member,
        user2: Optional[Member] = None,
    ):
        """The bot guesses how hot you are"""

        user2 = interaction.user if not user2 else user2

        seed((user1.id + user2.id) / 144)
        lovecalc = randint(0, 100)

        love_emoji = (
            "❤️‍🔥"
            if lovecalc >= 75
            else "❤️"
            if lovecalc >= 50
            else "❤️‍🩹"
            if lovecalc >= 25
            else "💔"
        )

        await interaction.response.send_message(
            f"{user1.mention} and {user2.mention} are compatible at `{lovecalc}%` {love_emoji} !"
        )

    @app_commands.command(name="useless_facts")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def useless_facts(self, interaction: discord.Interaction):
        r = request("GET", "https://uselessfacts.jsph.pl/random.json?language=en")
        if not r.ok:
            return await interaction.response.send_message(
                embed=Embed.error(description="Sorry, I could not fetch any facts.", delete_after=5)
            )

        embed = Embed(title="Useless facts", description=r.json()["text"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="horoscope")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(sign="Pick a class")
    @app_commands.choices(
        sign=[
            Choice(name="♈ Aries", value="aries"),
            Choice(name="♉ Taurus", value="taurus"),
            Choice(name="♊ Gemini", value="gemini"),
            Choice(name="♋ Cancer", value="cancer"),
            Choice(name="♌ Leo", value="leo"),
            Choice(name="♍ Virgo", value="virgo"),
            Choice(name="♎ Libra", value="libra"),
            Choice(name="♏ Scorpius", value="scorpio"),
            Choice(name="♐ Sagittarius", value="sagittarius"),
            Choice(name="♑ Capricorn", value="capricorn"),
            Choice(name="♒ Aquarius", value="aquarius"),
            Choice(name="♓ Pisces", value="pisces"),
        ]
    )
    async def horoscope(
        self,
        interaction: discord.Interaction,
        sign: Choice[str],
    ):
        """Get your daily horoscope"""
        sign = sign.value
        url = f"https://ohmanda.com/api/horoscope/{sign}"


        response = request("POST", url)
        r = response.json()

        embed = Embed(
            title=f":{sign.lower()}: Horoscope", description=f"{r['horoscope']}\n\n"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nerglish")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def nerglish(self, interaction: discord.Interaction, text: str):
        """Translate text to nerglish"""
        translated = NerglishTranslator.translate(text)
        await interaction.response.send_message(translated)

    @app_commands.command(name="lmgtfy")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def lmgtfy(self, interaction: discord.Interaction, text: str):
        """Let me google that for you"""
        await interaction.response.send_message(
            f"https://letmegooglethat.com/?q={urllib.parse.quote_plus(text)}"
        )
