import os
import importlib
from random import choice
import praw

from ether import *


class RedditCommandsManager:
    def __init__(self, client, client_id, client_secret, reddit_name, reddit_pass):
        self.client = client
        self.reddit_client = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="ether Bot",
            username=reddit_name,
            password=reddit_pass,
            check_for_async=False
        )

    def get_reddit_image(self, sub_reddit):
        sub = self.reddit_client.subreddit(sub_reddit)
        subs = [
            post
            for post in sub.hot(limit=100)
            if post.url.endswith(".png")
            or post.url.endswith(".jpg")
            or post.url.endswith(".gif")
            or post.url.endswith(".gifv")
        ]

        return choice(subs)


class LoaderManager:
    def __init__(self, bot):
        self.bot = bot

    async def find_extension(self):
        path = "ether/commands/"
        banned_dir = ["__pycache__"]
        name = "__init__.py"
        paths = [
            os.path.join(path, _dir)
            for _dir in os.listdir(path)
            if os.path.isdir(os.path.join(path, _dir)) and _dir not in banned_dir
        ]


        for path in paths:
            listdir = os.listdir(path)
            for file in listdir:
                if file == name:
                    mod = importlib.import_module(
                        path.replace("/", "."), package=__package__
                    )
                    try:
                        mod.setup(self.bot)
                        print(
                            f"\t[{paths.index(path)+1}/{len(paths)}] Commands loaded in {mod.__name__}"
                        )
                    except Exception as e:
                        raise e

class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"

class Colour:
    ERROR = 0xED4245
    SUCCESS = 0x57F287
    DEFAULT = 0x5865F2
    BAN = 0xED4245
    KICK = 0xFEE75C
    WARN = 0xFEE75C
    MUTE = 0xFEE75C
    UNBAN = 0x57F287
    UNMUTE = 0x57F287
    PRUNE = 0x5865F2