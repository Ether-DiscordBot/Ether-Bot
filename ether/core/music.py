from typing import Optional

import discord
import wavelink


class Player(wavelink.Player):
    def __init__(self, text_channel: Optional[discord.TextChannel]):
        super().__init__()
        self.message: Optional[discord.Message] = None
        self.text_channel = text_channel
        self.queue: wavelink.Queue = wavelink.Queue(max_size=100)
