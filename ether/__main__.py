import os

from dotenv import load_dotenv

from ether.client import Client, get_prefix

if __name__ == "__main__":
    load_dotenv()

    bot = Client(
        prefix=get_prefix,
        in_container=os.environ.get('IN_DOCKER', False)
    )

    bot.run(os.getenv('BOT_TOKEN'))
