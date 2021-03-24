from client import Client

import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    mochi_bot = Client()

mochi_bot.run(os.getenv('BOT_TOKEN'))
