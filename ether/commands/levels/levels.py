from discord.ext import commands
from discord import Embed, File
from ether import Color, MathsLevels
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import io, base64
import requests
import os


class Levels(commands.Cog, name="levels"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Levels"
        
        self.ch = CardHandler() # Card handler
    
    @commands.command(name="profile", aliases=["me", "rank", "level"])
    async def profile(self, ctx):
        user=self.client.db.get_guild_user(ctx.guild, ctx.author)
        if user:
            card=await self.ch.create_card(ctx.author, user)
            image=io.BytesIO(base64.b64decode(card))
            return await ctx.send(file=File(fp=image, filename=f"{ctx.author.name}_card.png"))
        return await ctx.send(embed=Embed(description="Error when trying to get your profile!", color=Color.ERROR))


class CardHandler:
    def __init__(self) -> None:
        self.pp_size=(120, 120)
        
        self.font = ImageFont.truetype(os.path.abspath("ether/src/fonts/whitneybold.otf"), 25)
        self.exp_font = ImageFont.truetype(os.path.abspath("ether/src/fonts/whitneybold.otf"), 15)
        self.level_font = ImageFont.truetype(os.path.abspath("ether/src/fonts/whitneybold.otf"), 35)
        self.backgrounds = [
            Image.open("ether/src/backgrounds/0.png")
        ]
        self.pp_mask=Image.new('L', self.pp_size, 0)
    
    async def create_card(self, user, db_user):
        img=Image.new(mode='RGBA', size=(600, 180), color=(255, 255, 255))
        
        img.paste(self.backgrounds[0].filter(ImageFilter.GaussianBlur(2)), (0, 0))
        
        # Profile Picture
        
        r = requests.get(user.avatar_url_as(format="png", size=128))
        pp=Image.open(io.BytesIO(r.content))
        pp=pp.resize(self.pp_size)
        
        pp_mask=Image.new('L', pp.size, 0)
        draw=ImageDraw.Draw(pp_mask)
        draw.ellipse((0, 0, pp.size[0]-1, pp.size[1]-1), fill=255)
        pp_mask.filter(ImageFilter.GaussianBlur(5))
        
        pp_padding=int((img.size[1]-self.pp_size[1])/2)
        img.paste(pp, (pp_padding, pp_padding), pp_mask)
        
        # Pseudo
        
        draw=ImageDraw.Draw(img)
        
        pseudo_left_padding=self.pp_size[1]+int(pp_padding*1.5)
        pseudo_top_padding=self.pp_size[1]-pp_padding*1.75
        
        draw.text((pseudo_left_padding, pseudo_top_padding-self.font.size/2), f"{user.name[:13]}", (255, 255, 255), self.font)
        draw.text((pseudo_left_padding+self.font.getsize(f"{user.name[:13]}")[0]+5, pseudo_top_padding-self.font.size/2), f"#{user.discriminator}", (210, 210, 210), self.font)
        
        # Exp bar
        
        max_size_bar=265
        line_width=14

        draw.rounded_rectangle((pseudo_left_padding, img.size[1]-pseudo_top_padding-line_width/2, pseudo_left_padding+max_size_bar, img.size[1]-pseudo_top_padding+line_width/2),
                        radius=line_width,
                        fill=(245, 246, 250),
                        width=0,
                        outline=None)
        
        exp_advancement=max_size_bar*db_user['exp']/MathsLevels.level_to_exp(db_user['levels']+1)
        draw.rounded_rectangle((pseudo_left_padding, img.size[1]-pseudo_top_padding-line_width/2, pseudo_left_padding+max(line_width, exp_advancement), img.size[1]-pseudo_top_padding+line_width/2),
                        radius=line_width,
                        fill=(246, 185, 59),
                        width=0,
                        outline=None)
        
        # Write level
        
        draw.text((pseudo_left_padding+max_size_bar+15, img.size[1]-pseudo_top_padding+line_width/2-self.font.size+3), "Level", (190, 190, 190), self.font)
        draw.text((pseudo_left_padding+max_size_bar+15+self.font.getsize("Level ")[0], img.size[1]-pseudo_top_padding+line_width/2-self.level_font.size+3), f"{db_user['levels']}", (255, 255, 255), self.level_font)
        
        # Write exp
        
        draw.text((pseudo_left_padding, img.size[1]-pseudo_top_padding-line_width/2+line_width+3), f"{db_user['exp']}", (255,255,255), self.exp_font)
        draw.text((pseudo_left_padding+self.exp_font.getsize(f"{db_user['exp']}")[0], img.size[1]-pseudo_top_padding-line_width/2+line_width+3), f"/{MathsLevels.level_to_exp(db_user['levels']+1)}exp", (190,190,190), self.exp_font)
        
        self._img=img
        
        # Convert to Base64
        
        with io.BytesIO() as buffer:
            self._img.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()
