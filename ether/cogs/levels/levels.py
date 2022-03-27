import base64
import io
import os

import requests
from PIL import Image, ImageDraw, ImageFont
from discord import File
from discord.ext import commands

from ether.core import MathsLevels


class Levels(commands.Cog, name="levels"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Levels"

        self.ch = CardHandler()

    @commands.command(name="profile", aliases=["me", "rank", "level"])
    async def profile(self, ctx):
        if not (user := self.client.db.get_guild_user(ctx.guild, ctx.author)):
            return await ctx.send_error("Error when trying to get your profile!")
        card = await self.ch.create_card(ctx.author, user)
        image = io.BytesIO(base64.b64decode(card))
        return await ctx.send(
            file=File(fp=image, filename=f"{ctx.author.name}_card.png")
        )


class CardHandler:
    BASE_FONT = ImageFont.truetype(
            os.path.abspath("ether/src/fonts/whitneybold.otf"), 25
        )
    EXP_FONT = ImageFont.truetype(
            os.path.abspath("ether/src/fonts/whitneybold.otf"), 15
        )
    LEVEL_FONT = ImageFont.truetype(
            os.path.abspath("ether/src/fonts/whitneybold.otf"), 35
        )
    
    def __init__(self) -> None:
        self.img_size = (600, 180)
        self.pp_size = (120, 120)
        self.pp_padding = (30, 30)

        mask = Image.open("ether/src/mask.png", 'r').convert('L').resize(self.img_size)
        background = Image.new("RGBA", self.img_size, 0)
        
        base_card = Image.new('RGBA', self.img_size, (48, 50, 56))
        
        draw = ImageDraw.Draw(base_card)
        
        level_padding = 445
        # "Level" label
        draw.text(
            xy=(level_padding, 120 - self.BASE_FONT.size + 2),
            # xy=(level_padding, self.blevel_y - self.BASE_FONT.size + 3),
            text="Level",
            fill=(190, 190, 190),
            font=self.BASE_FONT,
        )
        
        self.base_card = Image.composite(base_card, background, mask)
            
        self.pseudo_left_padding = 165
        self.pseudo_top_padding = 70

        self.max_size_bar = 265
        self.line_width = 15

    async def create_card(self, user, db_user):
        back = Image.new("RGBA", self.img_size, (245, 246, 250))
        
        # Profile Picture
        r = requests.get(user.avatar_url_as(format="png", size=128))
        pp = Image.open(io.BytesIO(r.content))
        pp = pp.resize(self.pp_size)
        
        back_draw = ImageDraw.Draw(back)
        
        # Advancement        
        exp_advancement = (
            self.max_size_bar
            * db_user["exp"]
            / MathsLevels.level_to_exp(db_user["levels"] + 1)
        )
        
        back_draw.rounded_rectangle(
            xy=(
                (165-2, 105),
                (
                    self.pseudo_left_padding + max(self.line_width, exp_advancement),
                    120,
                ),
            ),
            radius=self.line_width,
            fill=(246, 185, 59),
            width=0,
            outline=None,
        )
        
        back.paste(pp, self.pp_padding)
        img = Image.alpha_composite(back, self.base_card)
        
        
        draw = ImageDraw.Draw(img)
        
        # Pseudo
        # Name
        draw.text(
            xy=(self.pseudo_left_padding, self.pseudo_top_padding - self.BASE_FONT.size / 2),
            text=f"{user.name[:13]}",
            fill=(255, 255, 255),
            font=self.BASE_FONT,
        )

        # Discriminator
        draw.text(
            xy=(
                self.pseudo_left_padding
                + self.BASE_FONT.getsize(f"{user.name[:13]}")[0]
                + 5,
                self.pseudo_top_padding - self.BASE_FONT.size / 2,
            ),
            text=f"#{user.discriminator}",
            fill=(210, 210, 210),
            font=self.BASE_FONT,
        )

        # Write level
        # User level
        draw.text(
            xy=(
                505, # min 500
                120 - self.LEVEL_FONT.size + 2,
            ),
            text=f"{db_user['levels']}",
            fill=(255, 255, 255),
            font=self.LEVEL_FONT,
        )

        # Write exp
        # User exp
        draw.text(
            xy=(
                self.pseudo_left_padding, 120
            ),
            text=f"{db_user['exp']}",
            fill=(255, 255, 255),
            font=self.EXP_FONT,
        )

        # Max exp
        draw.text(
            xy=(
                self.pseudo_left_padding + self.EXP_FONT.getsize(f"{db_user['exp']}")[0],
                120
            ),
            text=f"/{MathsLevels.level_to_exp(db_user['levels'] + 1)} exp",
            fill=(190, 190, 190),
            font=self.EXP_FONT,
        )

        # Convert to Base64
        with io.BytesIO() as buffer:
            img.save(buffer, format="PNG", quality=75)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()
