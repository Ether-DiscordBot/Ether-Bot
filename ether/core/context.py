import optparse
import typing

from discord import Embed
from discord.ext import commands

from ether.core.constants import Colors

# TODO Move to ether/core/utils.py

# TODO EtherLogs

class EtherEmbeds():
    def error(message):
        return Embed(description=message, colour=Colors.ERROR)
