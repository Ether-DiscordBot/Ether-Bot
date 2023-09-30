from typing import Self

import discord

from mafic import Player, Track


class EtherPlayer(Player[discord.Bot]):
    def __init__(self, client: discord.Bot, channel: discord.VoiceChannel) -> None:
        super().__init__(client, channel)

        self.queue: Queue = Queue()
        self.loop: bool = False


class Queue(list[Track]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def is_empty(self) -> bool:
        return len(self) <= 0

    def get(self) -> Track:
        return self.pop(0)

    def copy(self) -> Self:
        return Queue(self)
