from discord.ext import commands
from discord import Embed

from core.reddit import get_reddit_image


def reddit_embed(post):
    embed = Embed(title=post.title)
    embed.url = "https://reddit.com/" + post.permalink
    embed.set_image(url=post.url)
    embed.set_footer(text=f"⬆️ {post.score} │ 💬 {post.num_comments}")

    return embed


class Image(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def meme(self, ctx):
        memes_subreddit = "memes"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any memes.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        memes_subreddit = "cats"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any cat pics.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx):
        memes_subreddit = "DOG"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any dog pics.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def aww(self, ctx):
        memes_subreddit = "aww"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any too cute pics.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sadcat(self, ctx):
        memes_subreddit = "sadcats"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any sad cat pics.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fan(self, ctx):
        memes_subreddit = "onlyfans"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any fans pics.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def axolotl(self, ctx):
        memes_subreddit = "axolotls"

        post = get_reddit_image(self.client, sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any axolotl pics.")
        else:
            embed = reddit_embed(post=post)

        return await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Image(client))