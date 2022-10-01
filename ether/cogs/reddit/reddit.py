import os

from discord import Embed, Interaction, Option, OptionChoice, SlashCommandGroup, TextChannel
from discord.ext import commands

from ether.core.constants import Colors
from ether.core.utils import EtherEmbeds
from ether.core.reddit import RedditPostCacher
from ether.core.logging import logging
from ether.core.config import config


class Reddit(commands.Cog, name="reddit"):
    def __init__(self, client) -> None:
        self.fancy_name = "🤖 Reddit"
        self.client = client
        self.subreddits = ("memes", "aww", "sadcats")
        cog_path = os.path.abspath("ether/cogs/reddit")
        self.cache = RedditPostCacher(config, self.subreddits, f"{cog_path}/cache.pickle")

    reddit = SlashCommandGroup("reddit", "Reddit commands!")

    async def _reddit(self, interaction: Interaction, subrd):
        post = await self.cache.get_random_post(subrd)

        if post.over_18:
            return None

        if post is None:
            logging.error(f"Reddit post image error with sub: {subrd}")
            return await interaction.response.send_message(
                embed=EtherEmbeds.error(
                    "😕 We are sorry, we have done a lot of research but we can't find any image."
                ),
                delete_after=5,
            )

        embed = Embed(title=post.title)
        if hasattr(post, "text"):
            embed.description = post.text
        embed.url = f"https://reddit.com{post.permalink}"
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

    @reddit.command(name="follow")
    @commands.has_permissions(manage_guild=True)
    async def follow(self, ctx, subreddit: str, channel: TextChannel,  nsfw: bool = False, rate: Option(int, "Choose how many posts will be posted", required=False, choices=[OptionChoice(name="Slow", value=1),
                                                                                                                                           OptionChoice(name="Medium", value=2),
                                                                                                                                           OptionChoice(name="Fast", value=3)]) = None):
        # TODO Follow a subreddit in a channel
        pass
    
    @reddit.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def _list(self, ctx):
        # TODO List all followed subereddits
        pass