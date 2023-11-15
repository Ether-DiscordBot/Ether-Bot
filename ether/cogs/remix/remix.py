import io
import os
import re

from discord import app_commands, File
import discord
from discord.ext.commands import Context
from discord.ext import commands
from PIL import Image as Img, ImageDraw, ImageFont

from ether.core.i18n import _
from ether.core.constants import Emoji


ASSETS_FOLDER_PATH = "ether/cogs/image/assets/"


class Remix(commands.Cog, name="remix"):
    def __init__(self, client) -> None:
        self.help_icon = Emoji.IMAGE
        self.client = client

    remix = app_commands.Group(name="remix", description="Remix memes")

    @remix.command(name="hold_up")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def hold_up(self, interaction: discord.Interaction, text: str):
        """Hold up!"""
        image = ImageModifier("hold-up.png")
        image.write(text, (10, 10), 30, 4)

        await interaction.response.send_message(
            file=File(fp=image.bytes, filename="hold-up.png")
        )

    @remix.command(name="vault-boy")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def vault_boy(self, interaction: discord.Interaction, up: str, bottom: str):
        """Vault boy meme"""
        image = ImageModifier("vault-boy.jpg")
        image.write(up, (200, 33), 25, 2, "mm")
        image.write(bottom, (200, 333), 25, 2, "mm")

        await interaction.response.send_message(
            file=File(fp=image.bytes, filename="vault_boy.jpg")
        )

    @remix.command(name="mr_incredible")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def mr_incredible(
        self, interaction: discord.Interaction, left: str, right: str
    ):
        """Mr Incredible meme"""
        image = ImageModifier("mr-incredible.png")
        image.write(left, (178, 365), 20, 1, "mm", fill=(255, 255, 255))
        image.write(right, (533, 365), 20, 1, "mm", fill=(255, 255, 255))

        await interaction.response.send_message(
            file=File(fp=image.bytes, filename="mr_incredible.png")
        )

    @remix.command(name="philosoraptor")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def philosoraptor(
        self, interaction: discord.Interaction, top: str, bottom: str
    ):
        """Philosoraptor meme"""
        image = ImageModifier("philosoraptor.png")
        image.write(top, (200, 33), 28, 2, "mm", fill=(255, 255, 255))
        image.write(bottom, (200, 333), 28, 2, "mm", fill=(255, 255, 255))

        await interaction.response.send_message(
            file=File(fp=image.bytes, filename="philosoraptor.png")
        )

    @remix.command(name="never_again")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def never_again(
        self, interaction: discord.Interaction, first: str, second: str, third: str
    ):
        """Never again meme"""
        image = ImageModifier("never_again.png")
        image.write(first, (125, 200), 15, 3, "mm", fill=(0, 0, 0))
        image.write(second, (350, 200), 15, 3, "mm", fill=(0, 0, 0))
        image.write(third, (100, 480), 15, 3, "mm", fill=(0, 0, 0))

        await interaction.response.send_message(
            file=File(fp=image.bytes, filename="never_again.png")
        )

    @remix.command(name="doom_bonked_zombie")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def doom_bonked_zombie(self, interaction: discord.Interaction, text: str):
        """Doom bonked zombie meme"""
        image = ImageModifier("doom_bonked_zombie.jpg")
        image.write(text, (400, 10), 30, 4, "ma", fill=(255, 255, 255))

        await interaction.response.send_message(
            file=File(fp=image.bytes, filename="doom_bonked_zombie.jpg")
        )


class ImageModifier:
    FONT = ImageFont.truetype(
        font=os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), size=30
    )

    def __init__(self, template_path: str) -> None:
        self.template = Img.open(os.path.join(ASSETS_FOLDER_PATH, template_path))

    def write(
        self,
        text: str,
        xy: tuple[int, int],
        max_words: int = 30,
        max_lines: int = -1,
        anchor="la",
        fill=(0, 0, 0),
    ):
        draw = ImageDraw.Draw(self.template)

        sentences = re.finditer(".{0," + str(max_words) + "}(\s+|$)", text)

        height = draw.textlength(text, ImageModifier.FONT, "ttb") + 5
        i = 0
        for match in sentences:
            splitted = match.group().split("\\n")
            for subs in splitted:
                if max_lines > 0 and i >= max_lines:
                    break
                draw.text(
                    (xy[0], xy[1] + height * i),
                    subs.strip(),
                    fill=fill,
                    font=ImageModifier.FONT,
                    anchor=anchor,
                )
                i += 1

    @property
    def bytes(self):
        with io.BytesIO() as buffer:
            self.template.save(buffer, format="PNG", quality=75)
            return io.BytesIO(buffer.getvalue())
