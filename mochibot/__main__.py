from client import Client

from dotenv import load_dotenv

load_dotenv()


def main(token=None, prefix=None):
    bot = Client(token, prefix)
    bot.run(bot.token)


if __name__ == "__main__":
    main()
