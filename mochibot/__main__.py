from client import Client

import os
from dotenv import load_dotenv

load_dotenv()


def main():
    mochi_bot = Client()
    mochi_bot.run(os.getenv('BOT_TOKEN'))


if __name__ == "__main__":
    main()
