from datetime import datetime
from typing import Any, Self

import discord
from discord.colour import Colour
from discord.types.embed import EmbedType

from ether.core.constants import Colors


class Embed(discord.Embed):
    def __init__(
        self,
        *,
        colour: int | Colour = Colors.DEFAULT,
        color: int | Colour | None = None,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ):
        super().__init__(
            colour=colour,
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )

    @classmethod
    def success(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        return Embed(
            colour=Colors.SUCCESS,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )

    @classmethod
    def error(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        return Embed(
            colour=Colors.ERROR,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )
