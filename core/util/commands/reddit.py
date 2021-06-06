from random import choice
import praw


class RedditCommandsManager:
    def __init__(self, client, client_id, client_secret, reddit_name, reddit_pass):
        self.client = client
        self.reddit_client = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="Mochi Bot",
            username=reddit_name,
            password=reddit_pass,
            check_for_async=False
        )

    def get_reddit_image(self, sub_reddit):
        sub = self.reddit_client.subreddit(sub_reddit)
        subs = []
        for post in sub.hot(limit=100):
            if post.url.endswith(".png") or post.url.endswith(".jpg") or post.url.endswith(".gif") or post.url.endswith(".gifv"):
                subs.append(post)
        return choice(subs)
