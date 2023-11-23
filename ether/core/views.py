import string
from typing import Callable, Optional

import discord

ascii_upper = string.ascii_uppercase

AlphabetSelectOptions = [
    discord.SelectOption(
        label=f'{ascii_upper[i]}-{ascii_upper[i + 1]}',
        value=(ascii_upper[i] + ascii_upper[i + 1]).lower(),
    )
    for i in range(0, 26, 2)
]

class AlphabetSelect(discord.ui.View):

    def __init__(self, *, callback: Callable, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)

        self.callback = callback


    @discord.ui.select(cls=discord.ui.Select, options=AlphabetSelectOptions)
    async def select_letter(self, interaction: discord.Interaction, select: discord.ui.Select):
        return await self.callback(interaction, select)
