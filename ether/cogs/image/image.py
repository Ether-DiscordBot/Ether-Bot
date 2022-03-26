import os
from random import choice

import requests
from discord.ext import tasks, commands
from discord import Embed
import praw

from ether.core import Color


class Post():
    def __init__(self, title, permalink, media_url, score, num_comments) -> None:
        self.title = title
        self.post_link = "https://reddit.com" + permalink
        self.media_url = media_url
        self.score = score
        self.num_comments = num_comments
    
    @property
    def embed(self) -> Embed:
        embed = Embed(title=self.title)
        embed.url = self.post_link
        embed.colour = Color.DEFAULT
        embed.set_image(url=self.media_url)
        embed.set_footer(text=f"⬆️ {self.score} │ 💬 {self.num_comments}")
        
        return embed


class Image(commands.Cog, name="image"):
    SUBREDDIT = ["memes", "cats", "DOG", "aww", "sadcats"]
    SUPPORTED_EMBED_FORMAT = ("jpg", "jpeg", "JPG", "JPEG", "png", "PNG", "gif", "gifv")
    
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Image"
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
    
    # TODO Optimize by creating a Reddit Post object and only store the information needed
    def fetch_reddit(self, sub):
        praw_posts = list(self.reddit.subreddit(sub).top("week"))
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

    async def embed_response(self, ctx, sub, err_msg):
        post = choice(getattr(self, f"{sub}_posts"))

        if post is None:
            await ctx.send_error(err_msg, delete_after=5)
            return

        return await ctx.send(embed=post.embed)

    @commands.command()
    async def gif(self, ctx, *, query):
        r = requests.get(
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
        r = requests.get(
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

    @commands.command()
    async def meme(self, ctx):
        memes_subreddit = "memes"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any memes."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    async def cat(self, ctx):
        memes_subreddit = "cats"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any cat pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    async def dog(self, ctx):
        memes_subreddit = "DOG"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any dog pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    async def aww(self, ctx):
        memes_subreddit = "aww"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any too cute pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    async def sadcat(self, ctx):
        memes_subreddit = "sadcats"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any sad cat pics."
        await self.embed_response(ctx, memes_subreddit, error_message)
