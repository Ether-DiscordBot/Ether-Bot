import io
import os
import re

from discord import File, SlashCommandGroup
from discord.ext import commands
from PIL import Image as Img, ImageDraw, ImageFont

ASSETS_FOLDER_PATH = "ether/cogs/image/assets/"
REGEX_LINES = r".{0,30}(\s+|$)"


class Image(commands.Cog, name="image"):
    def __init__(self, client) -> None:
        self.fancy_name = "Image"
        self.client = client
    
    image = SlashCommandGroup("image", "Image commands!")
    
    @image.command(name="hold_up")
    async def hold_up(self, ctx, text:str):
        image = ImageModifier("hold-up.png")
        image.write(text, (10, 10), 4)
        
        await ctx.respond(file=File(fp=image.bytes, filename=f"hold-up.png"))
        

class ImageModifier:
    FONT = ImageFont.truetype(os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 30)
    def __init__(self, template_path:str) -> None:
        self.template = Img.open(os.path.join(ASSETS_FOLDER_PATH, template_path))
    
    def write(self, text: str, xy: tuple[int, int], max_lines=-1):
        draw = ImageDraw.Draw(self.template)
        
        sentences = re.finditer(REGEX_LINES, text)

        height = draw.textsize("A", ImageModifier.FONT)[1] + 5
        i=0
        for match in sentences:
            splitted = match.group().split("\\n")
            for subs in splitted:
                if max_lines > 0 and i >= max_lines: break
                draw.text((xy[0], xy[1] + height*i), subs.strip(), fill=(0, 0, 0), font=ImageModifier.FONT)
                i+=1
    
    @property
    def bytes(self):
        with io.BytesIO() as buffer:
            self.template.save(buffer, format="PNG", quality=75)
            return io.BytesIO(buffer.getvalue())