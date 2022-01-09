from discord.ext import commands
from discord import Embed
from ether import Color


class Image(commands.Cog, name="image"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Image"

    async def embed_response(self, ctx, sub, err_msg):
        return await ctx.send(embed=Embed(description="This command is disabled. Retry later", color=Color.ERROR))
        
        post = self.client.redditCmd.get_reddit_image(sub_reddit=sub)

        if post is None:
            embed = Embed(color=Color.ERROR, description=err_msg)
        else:
            embed = Embed(title=post.title)
            embed.url = "https://reddit.com" + post.permalink
            embed.color = Color.DEFAULT
            embed.set_image(url=post.url)
            embed.set_footer(text=f"⬆️ {post.score} │ 💬 {post.num_comments}")

        return await ctx.send(embed=embed)

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