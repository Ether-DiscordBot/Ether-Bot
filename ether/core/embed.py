from datetime import datetime
from typing import Any, Optional, Self, Union

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


class DefaultEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        return super().__init__(
            colour=Colors.DEFAULT,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class ErrorEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.ERROR,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class SucessEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.SUCESS,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class BanEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.BAN,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class KickEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.KICK,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class WarnEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.WARN,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class MuteEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.MUTE,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class UnbanEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.UNBAN,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class UnmuteEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.UNMUTE,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )


class PruneEmbed(Embed):
    def __init__(
        cls,
        *,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None
    ) -> Self:
        super().__init__(
            colour=Colors.PRUNE,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )
