import os

from discord import Embed, Interaction, SlashCommandGroup
from discord.ext import commands

from ether.core.constants import Colors
from ether.core.context import EtherEmbeds
from ether.core.reddit import RedditPostCacher
from ether.core.logging import logging


class Reddit(commands.Cog):
    def __init__(self, client) -> None:
        self.fancy_name = "Reddit"
        self.client = client
        self.subreddits = ("memes", "aww", "sadcats")
        cog_path = os.path.abspath("ether/cogs/reddit")
        self.cache = RedditPostCacher(
            self.subreddits, f"{cog_path}/cache.pickle"
        )


    reddit = SlashCommandGroup("reddit", "Reddit commands!")

    async def _reddit(self, interaction: Interaction, subrd):
        post = await self.cache.get_random_post(subrd)

        if post.over_18:
            return None

        if post is None:
            logging.error(f"Reddit post image error with sub: {subrd}")
            return await interaction.response.send_message(embed=EtherEmbeds.error("😕 We are sorry, we have done a lot of research but we can't find any image."), delete_after=5)

        embed = Embed(title=post.title)
        if hasattr(post, "text"):
            embed.description = post.text
        embed.url = "https://reddit.com" + post.permalink
        embed.colour = Colors.DEFAULT
        embed.set_image(url=post.url)
        embed.set_footer(text=f"⬆️ {post.score} │ 💬 {post.num_comments}")

        await interaction.response.send_message(embed=embed)

    @reddit.command()
    async def meme(self, interaction: Interaction):
        await self._reddit(interaction, subrd="memes")

    @reddit.command()
    async def aww(self, interaction: Interaction):
        await self._reddit(interaction, subrd="aww")

    @reddit.command()
    async def sadcat(self, interaction: Interaction):
        await self._reddit(interaction, subrd="sadcats")
