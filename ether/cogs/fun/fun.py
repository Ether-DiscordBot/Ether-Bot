from random import choice
from requests import get, request
import os

from discord import (
    ApplicationCommand,
    Embed,
    Interaction,
    Option,
    OptionChoice,
    SlashCommandGroup,
)
from discord.ext import commands
from howlongtobeatpy import HowLongToBeat

from ether.core.utils import EtherEmbeds, NerglishTranslator


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
        self.help_icon = "🎡"
        self.client = client

        self.giphy_api_key = os.getenv("GIPHY_API_KEY")

    fun = SlashCommandGroup("fun", "Fun commands!")

    @fun.command()
    async def gif(self, interaction: Interaction, *, query):
        r = get(
            f"https://api.giphy.com/v1/gifs/random?tag={query}&api_key={self.giphy_api_key}"
        )

        r = r.json()
        if not r["data"]:
            await interaction.response.send_message(
                embed=EtherEmbeds.error(
                    "Sorry, I could not find any gifs with this query.", delete_after=5
                )
            )
            return
        gif_url = r["data"]["url"]

        await interaction.response.send_message(gif_url)

    @fun.command()
    async def sticker(self, interaction: Interaction, *, query):
        r = get(
            f"https://api.giphy.com/v1/stickers/random?tag={query}&api_key={self.giphy_api_key}"
        )

        r = r.json()
        if not r["data"]:
            await interaction.response.send_message(
                embed=EtherEmbeds.error(
                    "Sorry, I could not find any gifs with this query.", delete_after=5
                )
            )
            return
        sticker_url = r["data"]["images"]["original"]["url"]

        await interaction.response.send_message(sticker_url)

    @fun.command(name="8-ball")
    async def height_ball(self, interaction: Interaction, question: str):
        """
        Based on the standard Magic 8 Ball.
        """

        await interaction.response.send_message(
            f"🎱 {choice(choice(self.HEIGHT_BALL_ANSWERS))}"
        )

    @fun.command(name="say")
    async def say(
        self,
        interaction: Interaction,
        message: str,
        hide: Option(bool, "Hide ?", default=False),
    ):
        """
        Say what something the user want to.
        """

        if hide:
            await interaction.response.send_message(
                "👌 Done! (only you can see this message)",
                ephemeral=True,
                delete_after=5,
            )
            await interaction.channel.send(message)
            return

        await interaction.response.send_message(message)

    @fun.command(name="horoscope")
    async def horoscope(
        self,
        interaction: Interaction,
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

        url = "https://sameer-kumar-aztro-v1.p.rapidapi.com/"

        querystring = {"sign": sign, "day": "today"}

        headers = {
            "X-RapidAPI-Host": "sameer-kumar-aztro-v1.p.rapidapi.com",
            "X-RapidAPI-Key": os.getenv("AZTRO_API_KEY"),
        }

        response = request("POST", url, headers=headers, params=querystring)
        r = response.json()

        embed = Embed(
            title=f":{sign.lower()}: Horoscope",
            description=f"{r['description']}\n\n"
            f"**Compatibility:** {r['compatibility']}\n"
            f"**Mood:** {r['mood']}\n"
            f"**Luck:** Lucky number: {r['lucky_number']} | Lucky time: {r['lucky_time']}\n"
            f"**Color:** {r['color']}",
        )

        await interaction.response.send_message(embed=embed)

    @fun.command(name="nerglish")
    async def nerglish(self, ctx: ApplicationCommand, text: str):
        translated = NerglishTranslator.translate(text)
        await ctx.respond(translated)

    @fun.command(name="howlongtobeat")
    async def howlongtobeat(self, ctx: ApplicationCommand, game: str):
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
