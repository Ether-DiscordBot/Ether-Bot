from discord.ext import commands
from discord import Embed


class Image(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def meme(self, ctx):
        memes_subreddit = "memes"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any memes.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        memes_subreddit = "cats"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any cat pics.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx):
        memes_subreddit = "DOG"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any dog pics.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def aww(self, ctx):
        memes_subreddit = "aww"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any too cute pics.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sadcat(self, ctx):
        memes_subreddit = "sadcats"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any sad cat "
                                      "pics.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fan(self, ctx):
        memes_subreddit = "onlyfans"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any fans pics.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def axolotl(self, ctx):
        memes_subreddit = "axolotls"

        post = self.client.redditCmd.get_reddit_image(sub_reddit=memes_subreddit)

        if post is None:
            embed = Embed(description="😕 We are sorry, we have done a lot of research but we can't find any axolotl pics.")
        else:
            embed = self.client.redditCmd.reddit_embed(post=post)

        return await ctx.send(embed=embed)