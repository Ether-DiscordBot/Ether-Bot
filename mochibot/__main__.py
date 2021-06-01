import os

from mochibot.core import Client

from dotenv import load_dotenv

load_dotenv()


def main(prefix=None, token=None):
    bot = Client(prefix, token)
    bot.run(bot.token)


if __name__ == "__main__":
    main(os.getenv("BASE_PREFIX"), os.getenv("BOT_TOKEN"))
