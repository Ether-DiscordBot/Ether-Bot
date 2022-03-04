import os

import requests
from discord.ext import commands
from discord import Embed

from ether.core import Color


class Image(commands.Cog, name="image"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Image"
        self.giphy_api_key = os.getenv("GIPHY_API_KEY")

    async def embed_response(self, ctx, sub, err_msg):
        return await ctx.send(embed=Embed(description="This command is disabled. Retry later", color=Color.ERROR))
        
        post = self.client.redditCmd.get_reddit_image(sub_reddit=sub)

        if post is None:
            await ctx.send_error(err_msg, delete_after=5)
            return

        embed = Embed(title=post.title)
        embed.url = "https://reddit.com" + post.permalink
        embed.colour = Color.DEFAULT
        embed.set_image(url=post.url)
        embed.set_footer(text=f"⬆️ {post.score} │ 💬 {post.num_comments}")

        return await ctx.send(embed=embed)

    @commands.command()
    async def gif(self, ctx, *, query):
        r = requests.get(f"https://api.giphy.com/v1/gifs/random?tag={query}&api_key={self.giphy_api_key}")

        r = r.json()
        if not r['data']:
            await ctx.send_error("Sorry, I could not find any gifs with this query.", delete_after=5)
            return
        gif_url = r['data']['url']

        await ctx.send(gif_url)

    @commands.command()
    async def sticker(self, ctx, *, query):
        r = requests.get(f"https://api.giphy.com/v1/stickers/random?tag={query}&api_key={self.giphy_api_key}")

        r = r.json()
        if not r['data']:
            await ctx.send_error("Sorry, I could not find any stickers with this query.", delete_after=5)
            return
        sticker_url = r['data']['images']['original']['url']

        await ctx.send(sticker_url)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def meme(self, ctx):
        memes_subreddit = "memes"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any memes."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        memes_subreddit = "cats"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any cat pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx):
        memes_subreddit = "DOG"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any dog pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def aww(self, ctx):
        memes_subreddit = "aww"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any too cute pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sadcat(self, ctx):
        memes_subreddit = "sadcats"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any sad cat pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fans(self, ctx):
        memes_subreddit = "onlyfans"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any fans pics."
        await self.embed_response(ctx, memes_subreddit, error_message)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def axolotl(self, ctx):
        memes_subreddit = "axolotls"
        error_message = "😕 We are sorry, we have done a lot of research but we can't find any axolotl pics."
        await self.embed_response(ctx, memes_subreddit, error_message)
