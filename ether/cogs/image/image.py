import io
import os
import re

from discord import ApplicationContext, File, SlashCommandGroup
from discord.ext import commands
from PIL import Image as Img, ImageDraw, ImageFont
from ether.core.i18n import _

from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


ASSETS_FOLDER_PATH = "ether/cogs/image/assets/"


class Image(commands.Cog, name="image"):
    def __init__(self, client) -> None:
        self.help_icon = Emoji.IMAGE
        self.client = client

    image = SlashCommandGroup("image", "Image commands!")

    @image.command(name="hold_up")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def hold_up(self, ctx: ApplicationContext, text: str):
        """Hold up!"""
        image = ImageModifier("hold-up.png")
        image.write(text, (10, 10), 30, 4)

        await ctx.respond(file=File(fp=image.bytes, filename="hold-up.png"))

    @image.command(name="vault-boy")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def vault_boy(self, ctx: ApplicationContext, up: str, bottom: str):
        """Vault boy meme"""
        image = ImageModifier("vault-boy.jpg")
        image.write(up, (200, 33), 25, 2, "mm")
        image.write(bottom, (200, 333), 25, 2, "mm")

        await ctx.respond(file=File(fp=image.bytes, filename="vault_boy.jpg"))

    @image.command(name="mr_incredible")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def mr_incredible(self, ctx: ApplicationContext, left: str, right: str):
        """Mr Incredible meme"""
        image = ImageModifier("mr-incredible.png")
        image.write(left, (178, 365), 20, 1, "mm", fill=(255, 255, 255))
        image.write(right, (533, 365), 20, 1, "mm", fill=(255, 255, 255))

        await ctx.respond(file=File(fp=image.bytes, filename="mr_incredible.png"))

    @image.command(name="philosoraptor")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def philosoraptor(self, ctx: ApplicationContext, top: str, bottom: str):
        """Philosoraptor meme"""
        image = ImageModifier("philosoraptor.png")
        image.write(top, (200, 33), 28, 2, "mm", fill=(255, 255, 255))
        image.write(bottom, (200, 333), 28, 2, "mm", fill=(255, 255, 255))

        await ctx.respond(file=File(fp=image.bytes, filename="philosoraptor.png"))

    @image.command(name="never_again")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def never_again(
        self, ctx: ApplicationContext, first: str, second: str, third: str
    ):
        """Never again meme"""
        image = ImageModifier("never_again.png")
        image.write(first, (125, 200), 15, 3, "mm", fill=(0, 0, 0))
        image.write(second, (350, 200), 15, 3, "mm", fill=(0, 0, 0))
        image.write(third, (100, 480), 15, 3, "mm", fill=(0, 0, 0))

        await ctx.respond(file=File(fp=image.bytes, filename="never_again.png"))

    @image.command(name="doom_bonked_zombie")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @locale_doc
    async def doom_bonked_zombie(self, ctx: ApplicationContext, text: str):
        """Doom bonked zombie meme"""
        image = ImageModifier("doom_bonked_zombie.jpg")
        image.write(text, (400, 10), 30, 4, "ma", fill=(255, 255, 255))

        await ctx.respond(file=File(fp=image.bytes, filename="doom_bonked_zombie.jpg"))


class ImageModifier:
    FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 30
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

        height = draw.textsize("A", ImageModifier.FONT)[1] + 5
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
