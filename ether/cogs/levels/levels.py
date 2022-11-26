import base64
import io
import os
from typing import Optional
import discord

import requests
from PIL import Image, ImageDraw, ImageFont
from discord import SlashCommandGroup, Embed, Option, OptionChoice
from discord.file import File
from discord.ext import commands
from ether.core.i18n import _

from ether.core.utils import LevelsHandler, EtherEmbeds
from ether.core.db import Database, User, GuildUser, Guild
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


class Levels(commands.Cog, name="levels"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.LEVELS

    levels = SlashCommandGroup("levels", "levels commands!")

    @levels.command(name="boosters")
    @commands.has_permissions(moderate_members=True)
    @locale_doc
    async def boost(
        self,
        ctx,
        multiplier: Option(
            float, "Set the experience multiplier of this server (default: 1.0)"
        ),
    ) -> None:
        """Get the boosters of the server"""
        db_guild = await Guild.from_id(ctx.guild.id)

        if multiplier > 5:
            await ctx.respond("The multiplier must be less than 5.0")
            return
        elif multiplier < 0:
            await ctx.respond("The multiplier must be greater than 0.0")
            return

        await db_guild.set({Guild.exp_mult: multiplier})

        await ctx.respond(
            embed=EtherEmbeds.success(f"Experience multiplier set to `{multiplier}`!"),
            delete_after=5,
        )

    @levels.command(name="xp")
    @commands.has_permissions(moderate_members=True)
    @locale_doc
    async def xp(self, level: int = -1, xp: int = -1):
        """Set the xp or the level"""
        # TODO Set a user to a specific level or xp value
        pass

    @levels.command(name="leaderboard")
    @locale_doc
    async def leaderboard(self, ctx):
        """Get the leaderboard of the server"""
        members = await Database.GuildUser.get_all(ctx.guild.id, max=10)
        members.sort(key=lambda x: (x.levels, x.exp), reverse=True)

        embed = Embed(title=_("Leaderboard"), description="")
        i = 0
        for member in members:
            i += 1
            match i:
                case 1:
                    place = "🥇"
                case 2:
                    place = "🥈"
                case 3:
                    place = "🥉"
                case _:
                    place = f"#{i}"

            user = await ctx.guild.fetch_member(member.user_id)
            embed.description += f"{place} {user.mention} - Level **{member.levels}** | **{member.exp}** xp\n"

        await ctx.respond(embed=embed)

    @levels.command(name="set_background")
    @locale_doc
    async def set_background(
        self,
        ctx,
        background: Option(
            int,
            name="background",
            description="Choose the background of your rank card",
            choices=[
                OptionChoice("Grainy (default)", value=0),
                OptionChoice("Art Deco", value=1),
                OptionChoice("Rapture", value=2),
                OptionChoice("Mucha", value=3),
            ],
        ),
    ):
        """Set the background of your rank card"""
        db_user = await User.from_id(ctx.author.id)
        await db_user.set({User.background: background})

        await ctx.respond(
            embed=EtherEmbeds.success(_("✅ Your background has been changed!")),
            delete_after=5,
        )

    @levels.command(name="profile")
    @locale_doc
    async def profile(self, ctx, member: Optional[discord.Member] = None):
        """Get the profile of a user"""
        user = member if member else ctx.author
        db_guild_user = await GuildUser.from_member_object(user)
        db_user = await User.from_id(user.id)

        if not db_guild_user or not db_user:
            return await ctx.respond(
                embed=EtherEmbeds.error("Error when trying to get your profile!")
            )
        card = CardHandler.create_card(user, db_user, db_guild_user)
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

    BACKGROUNDS = [
        Image.open("ether/assets/backgrounds/grainy.png").convert("RGBA"),
        Image.open("ether/assets/backgrounds/art_deco.png").convert("RGBA"),
        Image.open("ether/assets/backgrounds/rapture.png").convert("RGBA"),
        Image.open("ether/assets/backgrounds/mucha.png").convert("RGBA"),
    ]

    def create_card(user, db_user, db_guild_user):
        img = CardHandler.BACKGROUNDS[db_user.background].copy()
        # Profile Picture
        r = requests.get(user.display_avatar)
        pp = Image.open(io.BytesIO(r.content))
        pp = pp.resize(CardHandler.MASK.size)

        # Advancement
        exp_advancement = (
            CardHandler.MAX_SIZE_BAR
            * db_guild_user.exp
            / LevelsHandler.get_next_level(db_guild_user.levels)
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

        level_size = draw.textsize(
            str(db_guild_user.levels), font=CardHandler.LEVEL_FONT
        )

        draw.text(
            xy=(
                228 + exp_advancement - (level_size[0] / 2) + 3,
                162 - (level_size[1] / 2),
            ),
            text=f"{db_guild_user.levels}",
            fill=(64, 64, 64),
            font=CardHandler.LEVEL_FONT,
        )

        # Pseudo
        # Name
        draw.text(
            xy=(228, 89),
            text=f"{user.name[:20]}",
            fill=(255, 255, 255),
            font=CardHandler.BASE_FONT,
        )

        # Discriminator
        draw.text(
            xy=(
                228 + CardHandler.BASE_FONT.getsize(f"{user.name[:20]}")[0] + 5,
                101,
            ),
            text=f"#{user.discriminator}",
            fill=(175, 175, 175),
            font=CardHandler.DISC_FONT,
        )

        # Experience
        exp_size = draw.textsize(str(db_guild_user.exp), CardHandler.EXP_FONT)
        draw.text(
            xy=(228, 183),
            text=f"{db_guild_user.exp}",
            fill=(255, 255, 255),
            font=CardHandler.EXP_FONT,
        )
        draw.text(
            xy=(228 + exp_size[0], 183),
            text=f"/{LevelsHandler.get_next_level(db_guild_user.levels)}exp",
            fill=(175, 175, 175),
            font=CardHandler.EXP_FONT,
        )

        # Convert to Base64
        with io.BytesIO() as buffer:
            img.save(buffer, format="PNG", quality=75)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()
