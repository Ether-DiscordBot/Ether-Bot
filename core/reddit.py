import requests
from random import randint, choice

limit = 1
pick = ['hot', 'new', 'best']


def get_reddit_image(sub_reddit, search_limit=100, retry=5):
    search_limit = min(search_limit, 100)
    url = f'https://api.reddit.com/r/{sub_reddit}/{choice(pick)}?limit={search_limit}'
    post = requests.get(url, headers={'User-agent': 'Mochi 0.1'}).json()
    rdn = randint(0, search_limit - 1)
    post = post['data']['children'][rdn]['data']

    if 'gallery_data' in post and post['gallery_data']:
        image_id = post['gallery_data']['items'][0]['media_id']
        image_url = f"https://i.redd.it/{image_id}.jpg"

    elif 'url' in post and post['url']:

        if post['url'].endswith('jpg') or post['url'].endswith('png'):
            image_url = post['url']
        elif retry <= 0:
            return
        else:
            return get_reddit_image(sub_reddit, retry=retry - 1)

    elif retry <= 0:
        return
    else:
        return get_reddit_image(sub_reddit, retry=retry-1)

    return {
        "id": post['id'],
        "title": post['title'],
        "uri": "https://redd.it/{}".format(post['id']),
        "image_uri": image_url,
        "thumbnail": post['thumbnail'],
        "subreddit": post['subreddit'],
        "NSFW": post['over_18'],
        "spoiler": post['spoiler'],
        "score": post['score'],
        "awards": post['total_awards_received'],
        "comments": post['num_comments']

    }
