from random import choice
import os
import praw
from discord import Embed


class RedditCommandsManager:
    def __init__(self):
        self.reddit_client = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="Mochi Bot",
            username=os.getenv('REDDIT_NAME'),
            password=os.getenv('REDDIT_PASS'),
            check_for_async=False
        )

    def get_reddit_image(self, sub_reddit):
        sub = self.reddit_client.subreddit(sub_reddit)
        subs = []
        for post in sub.hot(limit=100):
            if post.url.endswith(".png") or post.url.endswith(".jpg") or post.url.endswith(".gif") or post.url.endswith(".gifv"):
                subs.append(post)
        return choice(subs)

    def reddit_embed(self, post):
        embed = Embed(title=post.title)
        embed.url = "https://reddit.com" + post.permalink
        embed.set_image(url=post.url)
        embed.set_footer(text=f"⬆️ {post.score} │ 💬 {post.num_comments}")
        return embed
