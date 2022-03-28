from random import choice
from typing import Optional
from requests import request, get
import os

from discord import Embed, AllowedMentions
from discord.ext import tasks, commands
import praw

from ether.core import Color


class Post():
    def __init__(self, title, permalink, media_url, score, num_comments, text = None) -> None:
        self.title = title
        self.post_link = "https://reddit.com" + permalink
        self.media_url = media_url
        self.score = score
        self.num_comments = num_comments
        self.text = text
    
    @property
    def embed(self) -> Embed:
        embed = Embed(title=self.title)
        if self.text:
            embed.description = self.text
        embed.url = self.post_link
        embed.colour = Color.DEFAULT
        embed.set_image(url=self.media_url)
        embed.set_footer(text=f"⬆️ {self.score} │ 💬 {self.num_comments}")
        
        return embed


class Fun(commands.Cog):
    SUBREDDIT = ["memes", "cats", "DOG", "aww", "sadcats"]
    SUPPORTED_EMBED_FORMAT = ("jpg", "jpeg", "JPG", "JPEG", "png", "PNG", "gif", "gifv")
    HEIGHT_BALL_ANSWERS = [
        [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may reply on it.",
            "As I see it, yes.",
            "Most likely",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
        ],
        [
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
        ],
        [
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ],
    ]
    HOROSCOPE_SIGN = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]

    def __init__(self, client):
        self.fancy_name = "Fun"
        self.client = client
        
        self.giphy_api_key = os.getenv("GIPHY_API_KEY")
        
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="Ether Bot",
            check_for_async=False,
        )
        self.reddit.read_only = True
        
        for sub in self.SUBREDDIT:
            self.fetch_reddit(sub)
        
    def get_random_post(self, sub):
        post = self.reddit.subreddit(sub).random()
        
        if post.over_18 or post.url.endswith(self.SUPPORTED_EMBED_FORMAT):
            return None
        
        return Post(post.title, post.permalink, post.url, post.score, post.num_comments, post.selftext)
    
    def fetch_reddit(self, sub):
        praw_posts = list(self.reddit.subreddit(sub).top("day"))
        posts = []
        
        for post in praw_posts:
            if post.over_18:
                continue
            if post.url.endswith(self.SUPPORTED_EMBED_FORMAT):
                posts.append(Post(post.title, post.permalink, post.url, post.score, post.num_comments))
        
        setattr(self, f"{sub}_posts", posts)
    
    @tasks.loop(hours=1.0)
    async def fetch_loop(self):
        for sub in self.SUBREDDIT:
            self.fetch_reddit(sub)
    
    @commands.command()
    async def gif(self, ctx, *, query):
        r = get(
            f"https://api.giphy.com/v1/gifs/random?tag={query}&api_key={self.giphy_api_key}"
        )

        r = r.json()
        if not r["data"]:
            await ctx.send_error(
                "Sorry, I could not find any gifs with this query.", delete_after=5
            )
            return
        gif_url = r["data"]["url"]

        await ctx.send(gif_url)

    @commands.command()
    async def sticker(self, ctx, *, query):
        r = get(
            f"https://api.giphy.com/v1/stickers/random?tag={query}&api_key={self.giphy_api_key}"
        )

        r = r.json()
        if not r["data"]:
            await ctx.send_error(
                "Sorry, I could not find any stickers with this query.", delete_after=5
            )
            return
        sticker_url = r["data"]["images"]["original"]["url"]

        await ctx.send(sticker_url)

    @commands.command(name="8ball", aliases=["8-ball"])
    async def height_ball(self, ctx, question: str = None):
        """
        Based on the standard Magic 8 Ball.
        """

        if not question:
            return await ctx.reply(
                f"What would you ask to the Magic 8-Ball ?",
                allowed_mentions=AllowedMentions.none(),
            )

        await ctx.send(f"🎱 {choice(choice(self.HEIGHT_BALL_ANSWERS))}")

    @commands.command(name="say", aliases=["tell"])
    async def say(self, ctx, *, message):
        """
        Say what something the user want to.
        """

        options = ctx.get_options("hide")

        if options.get("hide"):
            message = message.replace("--hide", "")
            await ctx.message.delete()

        if len(message) <= 0:
            return await ctx.reply(
                f"What would you like me to say ?",
                allowed_mentions=AllowedMentions.none(),
            )

        await ctx.send(message)
        
    @commands.command(name="horoscope", aliases=["astro", "horo"])
    async def horoscope(self, ctx, sign: Optional[str] = None):
        if sign is None:
            return await ctx.reply(
                f"What is your astrological sign ?",
                allowed_mentions=AllowedMentions.none(),
                )
        if not sign.capitalize() in self.HOROSCOPE_SIGN:
            return await ctx.send_error(f"Incorrect sign, the astrological signs are:\n{', '.join(self.HOROSCOPE_SIGN)}")

        url = "https://sameer-kumar-aztro-v1.p.rapidapi.com/"

        querystring = {"sign": sign,"day":"today"}

        headers = {
            "X-RapidAPI-Host": "sameer-kumar-aztro-v1.p.rapidapi.com",
            "X-RapidAPI-Key": os.getenv("AZTRO_API_KEY")
        }

        response = request("POST", url, headers=headers, params=querystring)
        r = response.json()
        
        embed = Embed(title=f":{sign.lower()}: Horoscope", description=f"{r['description']}\n\n"
                              f"**Compatibility:** {r['compatibility']}\n"
                              f"**Mood:** {r['mood']}\n"
                              f"**Luck:** Lucky number: {r['lucky_number']} | Lucky time: {r['lucky_time']}\n"
                              f"**Color:** {r['color']}"
                              )

        await ctx.send(embed=embed)
    
    @commands.command(name="reddit")
    async def _reddit(self, ctx, sub):
        posts = getattr(self, f"{sub}_posts", None)
        
        if posts:
            post = choice(posts)
        else:
            post = self.get_random_post(sub)

        if post is None:
            await ctx.send_error("😕 We are sorry, we have done a lot of research but we can't find any image.", delete_after=5)
            return

        return await ctx.send(embed=post.embed)

    @commands.command()
    async def meme(self, ctx): await ctx.invoke(self._reddit, sub="memes")

    @commands.command()
    async def cat(self, ctx): await ctx.invoke(self._reddit, sub="cats")

    @commands.command()
    async def dog(self, ctx): await ctx.invoke(self._reddit, sub="DOG")

    @commands.command()
    async def aww(self, ctx): await ctx.invoke(self._reddit, sub="aww")

    @commands.command()
    async def sadcat(self, ctx): await ctx.invoke(self._reddit, sub="sadcats")