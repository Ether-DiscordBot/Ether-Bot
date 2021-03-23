from random import choice
import numpy as np

def get_reddit_image(client, sub_reddit):
    sub = client.reddit_client.subreddit(sub_reddit)
    subs = []
    for post in sub.hot(limit=100):
        if post.url.endswith(".png") or post.url.endswith(".jpg") or post.url.endswith(".gif") or post.url.endswith(".gifv"):
            subs.append(post)
    return choice(subs)
