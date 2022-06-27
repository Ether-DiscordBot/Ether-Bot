import io
import os
import re
from typing import Union

from discord import File, SlashCommandGroup
from discord.ext import commands
from PIL import Image as Img, ImageDraw, ImageFont

ASSETS_FOLDER_PATH = "ether/cogs/image/assets/"


class Image(commands.Cog, name="image"):
    def __init__(self, client) -> None:
        self.fancy_name = "📸 Image"
        self.client = client

    image = SlashCommandGroup("image", "Image commands!")

    @image.command(name="hold_up")
    async def hold_up(self, ctx, text: str):
        image = ImageModifier("hold-up.png")
        image.write(text, (10, 10), 30, 4)

        await ctx.respond(file=File(fp=image.bytes, filename=f"hold-up.png"))

    @image.command(name="vault-boy")
    async def vault_boy(self, ctx, up: str, bottom: str):
        image = ImageModifier("vault-boy.jpg")
        image.write(up, (200, 33), 25, 2, "mm")
        image.write(bottom, (200, 333), 25, 2, "mm")

        await ctx.respond(file=File(fp=image.bytes, filename=f"vault_boy.jpg"))

    @image.command(name="mr_incredible")
    async def mr_incredible(self, ctx, left: str, right: str):
        image = ImageModifier("mr-incredible.png")
        image.write(left, (178, 365), 20, 1, "mm", fill=(255, 255, 255))
        image.write(right, (533, 365), 20, 1, "mm", fill=(255, 255, 255))

        await ctx.respond(file=File(fp=image.bytes, filename=f"mr_incredible.png"))


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
