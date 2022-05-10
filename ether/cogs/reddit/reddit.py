from discord import Embed
from discord.ext import commands

from ether.core.constants import Colors
from ether.core.reddit import RedditPostCacher


class Reddit(commands.Cog):
    def __init__(self, client) -> None:
        self.fancy_name = "Reddit"
        self.client = client
        self.subreddits = ( "memes", "aww", "sadcats" )
        self.cache = RedditPostCacher(
            self.subreddits, "ether/cogs/fun/cache.pickle"
        )
        
        self.cache.cache_posts.start()
        
    
    
    async def _reddit(self, ctx, subrd):
        post = await self.cache.get_random_post(subrd)

        if post.over_18: return None

        if post is None:
            await ctx.send_error(
                "😕 We are sorry, we have done a lot of research but we can't find any image.",
                delete_after=5,
            )
            return

        embed = Embed(title=post.title)
        if hasattr(post, "text"):
            embed.description = post.text
        embed.url = "https://reddit.com" + post.permalink
        embed.colour = Colors.DEFAULT
        embed.set_image(url=post.url)
        embed.set_footer(text=f"⬆️ {post.score} │ 💬 {post.num_comments}")

        return await ctx.send(embed=embed)
    
    @commands.command()
    async def meme(self, ctx):
        await ctx.invoke(self._reddit, subrd="memes")

    @commands.command()
    async def aww(self, ctx):
        await ctx.invoke(self._reddit, subrd="aww")

    @commands.command()
    async def sadcat(self, ctx):
        await ctx.invoke(self._reddit, subrd="sadcats")