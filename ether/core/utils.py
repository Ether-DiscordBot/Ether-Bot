import os
import importlib
from random import choice
import praw
import math


class MathsLevels:
    def get_level(level, exp):
        return int(math.sqrt(max(MathsLevels.level_to_exp(level)+exp, 1))*0.2)

    def level_to_exp(level):
        return 50*pow(level-1, 2)


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

class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"

class Color:
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