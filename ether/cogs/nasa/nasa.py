import os
import random
import requests

from discord import Embed, Option, OptionChoice, SlashCommandGroup
from discord.ext import commands

from ether.core.utils import EtherEmbeds


class Nasa(commands.Cog, name="nasa"):
    def __init__(self, client) -> None:
        self.fancy_name = "🛰️ Nasa"
        self.client = client
        self.api_key = os.environ["NASA_API_KEY"]

    nasa = SlashCommandGroup("nasa", "Nasa commands!")

    @nasa.command(name="apod")
    async def apod(self, ctx):
        r = requests.get(
            f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&thumbs=true"
        )

        if not r.ok:
            return ctx.respond(embed=EtherEmbeds.error("Sorry, an error has occurred."))

        res = r.json()

        image = None
        if res["media_type"] == "video":
            if res["thumbnail_url"]:
                image = res["thumbnail_url"]
        elif res["media_type"] == "image":
            image = res["hdurl"]
        else:
            return ctx.respond(
                embed=EtherEmbeds.error("Sorry, unknow media type."), delete_after=5
            )

        embed = Embed(title=res["title"], url=res["url"])
        embed.set_footer(text="Powered by Nasa")
        if image:
            embed.set_image(url=image)

        await ctx.respond(embed=embed)

    @nasa.command(name="epic")
    async def epic(self, ctx, faces: int = 1):
        if faces > 20:
            return await ctx.respond(
                embed=EtherEmbeds.error("Faces must be between 1 and 20."),
                delete_after=5,
            )

        r = requests.get(
            f"https://api.nasa.gov/EPIC/api/natural/images?api_key={self.api_key}"
        )

        if not r.ok:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error has occurred."), delete_after=5
            )

        res = r.json()
        res = res[faces]

        date = res["date"].split(" ")[0].split("-")
        image = f"https://epic.gsfc.nasa.gov/archive/natural/{date[0]}/{date[1]}/{date[2]}/png/{res['image']}.png"

        embed = Embed(title="Epic", description=res["caption"])
        embed.set_image(url=image)
        embed.set_footer(text="Powered by Nasa")

        await ctx.respond(embed=embed)

    @nasa.command(name="mars")
    async def mars(
        self,
        ctx,
        rover: Option(
            str,
            "Rover on Mars",
            required=True,
            choices=[
                OptionChoice("Curiosity", value="curiosity"),
                OptionChoice("Opportunity", value="opportunity"),
                OptionChoice("Spirit", value="spirit"),
            ],
        ),
    ):
        r = requests.get(
            f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?sol=1000&api_key={self.api_key}"
        )

        if not r.ok:
            return ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error has occurred."), delete_after=5
            )

        res = r.json()
        photo = random.choice(res["photos"])

        embed = Embed(
            title=f"Mars {rover} photo",
            description=f"**camera:** {photo['camera']['full_name']}\n**date:** {photo['earth_date']}",
        )
        embed.set_image(url=photo["img_src"])
        embed.set_footer(text="Powered by Nasa")

        await ctx.respond(embed=embed)
