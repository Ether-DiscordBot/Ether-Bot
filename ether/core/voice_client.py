import discord
from mafic import Player, Track

from ether.core import config


class EtherPlayer(Player[discord.Bot]):
    def __init__(self, client: discord.Bot, channel: discord.VoiceChannel) -> None:
        super().__init__(client, channel)

        self.queue: list[Track] = []
