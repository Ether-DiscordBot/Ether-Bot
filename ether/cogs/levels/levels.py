import base64
import io
import os
import discord

import requests
from PIL import Image, ImageDraw, ImageFont
from discord import File, SlashCommandGroup
from discord.ext import commands
from pycord18n.extension import _

from ether.core.utils import LevelsHandler, EtherEmbeds
from ether.core.db import Database
from ether.core.i18n import locale_doc


class Levels(commands.Cog, name="levels"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "📈 Levels"
        self.help_icon = "📈"

    levels = SlashCommandGroup("levels", "levels commands!")

    @levels.command(name="boosters")
    @locale_doc
    async def boosters(self, ctx):
        """Get the boosters of the server"""
        # TODO View all xp roles booster in the server
        pass

    @levels.command(name="xp")
    @commands.has_permissions(moderate_members=True)
    @locale_doc
    async def xp(self, level: int = -1, xp: int = -1):
        """Set the xp or the level"""
        # TODO Set a user to a specific level or xp value
        pass

    @levels.command(name="profile")
    @locale_doc
    async def profile(self, ctx, user: discord.Member = None):
        """Get the profile of a user"""
        user = user if user else ctx.user
        dbuser = (
            await Database.GuildUser.get_or_create(  # FIXME Always return the same user
                user.id, ctx.guild_id
            )
        )
        if not dbuser:
            return await ctx.respond(
                embed=EtherEmbeds.error("Error when trying to get your profile!")
            )
        card = CardHandler.create_card(user, dbuser)
        image = io.BytesIO(base64.b64decode(card))
        return await ctx.respond(file=File(fp=image, filename=f"{user.name}_card.png"))


class CardHandler:
    BASE_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 44
    )
    DISC_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 29
    )
    LEVEL_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Bold.ttf"), 22
    )
    EXP_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Bold.ttf"), 19
    )
    MASK = Image.open("ether/assets/mask.png", "r").convert("L")
    MAX_SIZE_BAR = 634

    def create_card(self, db_user):
        img = Image.open("ether/assets/background.png").convert("RGBA")
        # Profile Picture
        r = requests.get(self.display_avatar)
        pp = Image.open(io.BytesIO(r.content))
        pp = pp.resize(CardHandler.MASK.size)

        # Advancement
        exp_advancement = (
            CardHandler.MAX_SIZE_BAR
            * db_user.exp
            / LevelsHandler.get_next_level(db_user.levels)
        )

        img.paste(pp, (34, 56), CardHandler.MASK)

        draw = ImageDraw.Draw(img)

        draw.rectangle(
            xy=(
                (228 + 4, 157),
                (228 + exp_advancement, 157 + 14 + 3),
            ),
            fill=(236, 185, 125),
        )

        draw.rectangle(
            xy=(
                (228 + 4, 157),
                (228 + 634, 157 + 14 + 3),
            ),
            fill=None,
            width=4,
            outline=(255, 255, 255),
        )

        draw.ellipse(
            xy=(
                228 + exp_advancement - 20 + 2,
                144,
                228 + exp_advancement + 20 + 2,
                144 + 40,
            ),
            fill=(236, 185, 125),
            width=4,
            outline=(255, 255, 255),
        )

        level_size = draw.textsize(str(db_user.levels), font=CardHandler.LEVEL_FONT)

        draw.text(
            xy=(
                228 + exp_advancement - (level_size[0] / 2) + 3,
                162 - (level_size[1] / 2),
            ),
            text=f"{db_user.levels}",
            fill=(64, 64, 64),
            font=CardHandler.LEVEL_FONT,
        )

        # Pseudo
        # Name
        draw.text(
            xy=(228, 89),
            text=f"{self.name[:13]}",
            fill=(255, 255, 255),
            font=CardHandler.BASE_FONT,
        )

        # Discriminator
        draw.text(
            xy=(
                228 + CardHandler.BASE_FONT.getsize(f"{self.name[:13]}")[0] + 5,
                101,
            ),
            text=f"#{self.discriminator}",
            fill=(175, 175, 175),
            font=CardHandler.DISC_FONT,
        )

        # Experience
        exp_size = draw.textsize(str(db_user.exp), CardHandler.EXP_FONT)
        draw.text(
            xy=(228, 183),
            text=f"{db_user.exp}",
            fill=(255, 255, 255),
            font=CardHandler.EXP_FONT,
        )
        draw.text(
            xy=(228 + exp_size[0], 183),
            text=f"/{LevelsHandler.get_next_level(db_user.levels)}exp",
            fill=(175, 175, 175),
            font=CardHandler.EXP_FONT,
        )

        # Convert to Base64
        with io.BytesIO() as buffer:
            img.save(buffer, format="PNG", quality=75)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()
