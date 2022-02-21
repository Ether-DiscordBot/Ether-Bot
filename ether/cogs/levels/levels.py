import base64
import io
import os

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from discord import Embed, File
from discord.ext import commands

from ether import Color, MathsLevels


class Levels(commands.Cog, name="levels"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Levels"
        
        self.ch = CardHandler()
    
    @commands.command(name="profile", aliases=["me", "rank", "level"])
    async def profile(self, ctx):
        if user := self.client.db.get_guild_user(ctx.guild, ctx.author):
            card=await self.ch.create_card(ctx.author, user)
            image=io.BytesIO(base64.b64decode(card))
            return await ctx.send(file=File(fp=image, filename=f"{ctx.author.name}_card.png"))
        return await ctx.send(embed=Embed(description="Error when trying to get your profile!", color=Color.ERROR))


class CardHandler:
    def __init__(self) -> None:
        self.img_size=(600, 180)
        self.pp_size=(120, 120)
        
        self.font = ImageFont.truetype(os.path.abspath("ether/src/fonts/whitneybold.otf"), 25)
        self.exp_font = ImageFont.truetype(os.path.abspath("ether/src/fonts/whitneybold.otf"), 15)
        self.level_font = ImageFont.truetype(os.path.abspath("ether/src/fonts/whitneybold.otf"), 35)
        self.backgrounds = [
            Image.open("ether/src/backgrounds/0.png")
        ]
        self.pp_mask=Image.new('L', self.pp_size, 0)
        
        self.pp_padding=int((self.img_size[1]-self.pp_size[1])/2)
        
        self.pseudo_left_padding=self.pp_size[1]+int(self.pp_padding*1.5)
        self.pseudo_top_padding=self.pp_size[1]-self.pp_padding*1.75
        
        self.max_size_bar=265
        self.line_width=14
        
        self.exp_xy1=(self.pseudo_left_padding, self.img_size[1]-self.pseudo_top_padding-self.line_width/2)
        self.exp_y2=self.img_size[1]-self.pseudo_top_padding+self.line_width/2
        
        self.level_padding=self.pseudo_left_padding+self.max_size_bar+15
        self.blevel_y=self.img_size[1]-self.pseudo_top_padding+self.line_width/2
    
    async def create_card(self, user, db_user):
        img=Image.new(mode='RGBA', size=self.img_size, color=(255, 255, 255))
        
        img.paste(self.backgrounds[0].filter(ImageFilter.GaussianBlur(2)), (0, 0))
        
        # Profile Picture
        r = requests.get(user.avatar_url_as(format="png", size=128))
        pp=Image.open(io.BytesIO(r.content)) # pp => profile picture
        pp=pp.resize(self.pp_size)
        
        pp_mask=Image.new('L', pp.size, 0)
        draw=ImageDraw.Draw(pp_mask)
        draw.ellipse((0, 0, pp.size[0]-1, pp.size[1]-1), fill=255)
        pp_mask.filter(ImageFilter.GaussianBlur(5))
        
        img.paste(pp, (self.pp_padding, self.pp_padding), pp_mask) # Paste the circle mask on the profile picture
        
        
        draw=ImageDraw.Draw(img) # Make the image drawable
        
        # Pseudo
            # Name
        draw.text(
            xy=(self.pseudo_left_padding, self.pseudo_top_padding-self.font.size/2),
            text=f"{user.name[:13]}",
            fill=(255, 255, 255),
            font=self.font)

            # Discriminator
        draw.text(
            xy=(self.pseudo_left_padding+self.font.getsize(f"{user.name[:13]}")[0]+5, self.pseudo_top_padding-self.font.size/2),
            text=f"#{user.discriminator}",
            fill=(210, 210, 210), 
            font=self.font)
        
        # Exp bar
        exp_advancement=self.max_size_bar*db_user['exp']/MathsLevels.level_to_exp(db_user['levels']+1)
            # Background
        draw.rounded_rectangle(
            xy=(self.exp_xy1,
                (self.pseudo_left_padding+self.max_size_bar, self.exp_y2)),
            radius=self.line_width,
            fill=(245, 246, 250),
            width=0,
            outline=None)
        
            # Advancement
        draw.rounded_rectangle(
            xy=(self.exp_xy1,
                (self.pseudo_left_padding+max(self.line_width, exp_advancement), self.exp_y2)),
            radius=self.line_width,
            fill=(246, 185, 59),
            width=0,
            outline=None)
        
        # Write level
            # "Level" label
        draw.text(
            xy=(self.level_padding, self.blevel_y-self.font.size+3),
            text="Level",
            fill=(190, 190, 190),
            font=self.font)
            # User level
        draw.text(
            xy=(self.level_padding+self.font.getsize("Level ")[0], self.blevel_y-self.level_font.size+3),
            text=f"{db_user['levels']}",
            fill=(255, 255, 255),
            font=self.level_font)
        
        # Write exp
            # User exp
        draw.text(
            xy=(self.pseudo_left_padding, self.img_size[1]-self.pseudo_top_padding-self.line_width/2+self.line_width+3),
            text=f"{db_user['exp']}",
            fill=(255,255,255),
            font=self.exp_font)
        
            # Max exp
        draw.text(
            xy=(self.pseudo_left_padding+self.exp_font.getsize(f"{db_user['exp']}")[0], img.size[1]-self.pseudo_top_padding-self.line_width/2+self.line_width+3),
            text=f"/{MathsLevels.level_to_exp(db_user['levels']+1)}exp",
            fill=(190,190,190),
            font=self.exp_font)
        
        self._img=img
        
        # Convert to Base64
        with io.BytesIO() as buffer:
            self._img.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()
