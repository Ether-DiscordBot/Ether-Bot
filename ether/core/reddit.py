import asyncio
import os
import random
import aiofiles
import pickle

from discord.ext import tasks
from typing import List, Tuple

from asyncpraw import Reddit
from asyncpraw.models import Submission, Subreddit

from ether.core.logging import log


class RedditPostCacher:
    def __init__(self, subreddit_names: List[str], cache_location) -> None:
        self.subreddit_names = subreddit_names

        self.file_path = cache_location

        self.reddit = Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="Ether Bot",
        )

        self.run()
    
    def run(self):
        asyncio.run(self.cache_posts())

    async def cache_subreddit(self, subreddit: Subreddit) -> Tuple[str, List[str]]:
        """Caches top posts from a subreddit
        Parameters
        ----------
        subreddit : Subreddit
            The subreddit to cache posts from
        Returns
        -------
        Tuple[str, List[str]]
            A tuple of subreddit name and list of post URLs
        """
        await subreddit.load()
        posts = [post async for post in subreddit.hot(limit=50)]
        allowed_extensions = (".gif", ".png", ".jpg", ".jpeg")
        posts = list(
            filter(
                lambda i: any(i.url.endswith(e) for e in allowed_extensions),
                posts,
            )
        )
        posts = [post.id for post in posts]
        return (subreddit.display_name, posts)

    @tasks.loop(minutes=30)
    async def cache_posts(self) -> None:
        subreddits = [
            await self.reddit.subreddit(subreddit) for subreddit in self.subreddit_names
        ]
        tasks = tuple(self.cache_subreddit(subreddit) for subreddit in subreddits)
        all_sub_content = await asyncio.gather(*tasks)
        data_to_dump = dict(all_sub_content)

        async with aiofiles.open(self.file_path, mode="wb+") as f:
            await f.write(pickle.dumps(data_to_dump))

        log.info(f"Posts from {len(subreddits)} subreddits has been cached.")

    async def get_random_post(self, subreddit: str) -> Submission:
        """Fetches a post from the internal cache
        Parameters
        ----------
        subreddit : str
            The name of the subreddit to fetch from
        Returns
        -------
        asyncpraw.models.Submission
            The randomly chosen submission
        Raises
        ------
        ValueError
            The subreddit was not in the internal cache
        """
        if not os.path.exists(self.file_path):
            print("path doesn't exist")
            await self.cache_posts()

        async with aiofiles.open(self.file_path, mode="rb") as f:
            cache = pickle.loads(await f.read())
            try:
                subreddit = cache[subreddit]
            except KeyError as e:
                raise ValueError("Subreddit not in cache!") from e
            else:
                random_post = self.reddit.submission(random.choice(subreddit))
                return await random_post
