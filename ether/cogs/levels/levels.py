import base64
import io
import os
from typing import Optional

import discord
import requests
from discord import File, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Context
from PIL import Image, ImageDraw, ImageFont

from ether.core.constants import Emoji
from ether.core.db import Database, Guild, GuildUser, User
from ether.core.embed import Embed, ErrorEmbed
from ether.core.i18n import _
from ether.core.utils import LevelsHandler


class Levels(commands.GroupCog, name="levels"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.LEVELS

    @app_commands.command(name="boosters")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        multiplier="Set the experience multiplier of this server (default: 1.0)"
    )
    async def boost(self, interaction: discord.Interaction, multiplier: float) -> None:
        """Get the boosters of the server"""
        db_guild = await Guild.from_id(interaction.guild.id)

        if multiplier > 5:
            await interaction.response.send_message(
                "The multiplier must be less than 5.0"
            )
            return
        elif multiplier < 0:
            await interaction.response.send_message(
                "The multiplier must be greater than 0.0"
            )
            return

        await db_guild.set({Guild.exp_mult: multiplier})

        await interaction.response.send_message(
            embed=Embed.success(f"Experience multiplier set to `{multiplier}`!"),
            delete_after=5,
        )

    @app_commands.command(name="xp")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def xp(self, interaction: discord.Interaction, level: int = -1, xp: int = -1):
        """Set the xp or the level"""
        # TODO Set a user to a specific level or xp value

    @app_commands.command(name="leaderboard")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def leaderboard(self, interaction: discord.Interaction):
        """Get the leaderboard of the server"""
        members = await Database.GuildUser.get_all(interaction.guild.id, max=10)
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

            user = await interaction.guild.fetch_member(member.user_id)
            embed.description += f"{place} {user.mention} - Level **{member.levels}** | **{member.exp}** xp\n"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set_background")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(background="Choose the background of your rank card")
    @app_commands.choices(
        background=[
            Choice(name="Grainy (default)", value=0),
            Choice(name="Art Deco", value=1),
            Choice(name="Rapture", value=2),
            Choice(name="Mucha", value=3),
        ]
    )
    async def set_background(
        self,
        interaction: discord.Interaction,
        background: Choice[int],
    ):
        """Set the background of your rank card"""
        db_user = await User.from_id(interaction.user.id)
        await db_user.set({User.background: background})

        await interaction.response.send_message(
            embed=Embed.success(_("✅ Your background has been changed!")),
            delete_after=5,
        )

    @app_commands.command(name="profile")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def profile(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Get the profile of a user"""
        user = member if member else interaction.user
        db_guild_user = await GuildUser.from_member_object(user)
        db_user = await User.from_id(user.id)

        if not db_guild_user or not db_user:
            return await interaction.response.send_message(
                embed=ErrorEmbed("Error when trying to get your profile!")
            )
        card = CardHandler.create_card(user, db_user, db_guild_user)
        image = io.BytesIO(base64.b64decode(card))
        return await interaction.response.send_message(
            file=File(fp=image, filename=f"{user.name}_card.png")
        )


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

    @classmethod
    def create_card(cls, user, db_user, db_guild_user):
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

        level_size_width = draw.textlength(
            str(db_guild_user.levels), CardHandler.LEVEL_FONT, "rtl"
        )

        level_size_height = draw.textlength(
            str(db_guild_user.levels), CardHandler.LEVEL_FONT, "ttb"
        )

        draw.text(
            xy=(
                228 + exp_advancement - (level_size_width / 2) + 3,
                162 - (level_size_height / 2),
            ),
            text=f"{db_guild_user.levels}",
            fill=(64, 64, 64),
            font=CardHandler.LEVEL_FONT,
        )

        # Pseudo
        # Global name
        draw.text(
            xy=(228, 89),
            text=f"{user.global_name[:20]}",
            fill=(255, 255, 255),
            font=CardHandler.BASE_FONT,
        )

        # Name
        draw.text(
            xy=(
                228
                + CardHandler.BASE_FONT.getlength(f"{user.global_name[:20]} ", direction="rtl"),
                101,
            ),
            text=f"{user.name}",
            fill=(175, 175, 175),
            font=CardHandler.DISC_FONT,
        )

        # Experience
        exp_size_width = draw.textlength(
            str(db_guild_user.exp), CardHandler.EXP_FONT, "rtl"
        )
        draw.text(
            xy=(228, 183),
            text=f"{db_guild_user.exp}",
            fill=(255, 255, 255),
            font=CardHandler.EXP_FONT,
        )
        draw.text(
            xy=(228 + exp_size_width, 183),
            text=f"/{LevelsHandler.get_next_level(db_guild_user.levels)}exp",
            fill=(175, 175, 175),
            font=CardHandler.EXP_FONT,
        )

        # Convert to Base64
        with io.BytesIO() as buffer:
            img.save(buffer, format="PNG", quality=75)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()
