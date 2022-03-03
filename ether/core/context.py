import optparse
import typing

from discord import Embed
from discord.ext import commands

from ether.core import Color


class Options:
    def __init__(self, options: typing.Optional[dict] = None):
        if options is None:
            return

        for key, value in options.items():
            setattr(self, key, value)

    def get(self, attr):
        return getattr(self, attr, False)


class EtherContext(commands.Context):
    def get_options(self, *opts):
        parser = optparse.OptionParser()
        message = self.message.content.split()

        if not any(o for o in opts if o in self.message.content):
            return Options()

        for opt in opts:
            parser.add_option(f"--{opt}",
                              action="store_true", default=False)

        try:
            options = parser.parse_args(message)
        except SystemExit:
            return Options()
        return Options(options[0].__dict__)

    async def send_error(self, message, delete_after=None):
        await self.send(embed=Embed(description=message, colour=Color.ERROR), delete_after=delete_after)
