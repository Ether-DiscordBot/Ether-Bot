import asyncio

from discord import Intents
import discord
from discord.ext import commands
import wavelink

from ether import __version__
from ether.core.config import config
from ether.core.cog_manager import CogManager
from ether.core.logging import log
from ether.core.constants import NODE_CODE_NAME


class Ether(commands.bot.AutoShardedBot):
    """The Ether subclass of discord.ext.commands.bot.AutoSharedBot"""

    def __init__(self, *, cli_flags=None, **kwargs) -> None:
        intents = Intents.all()
        super().__init__(
            command_prefix=None, intents=intents, help_command=None, **kwargs
        )

    async def add_cog(self, cog: commands.Cog) -> None:
        await super().add_cog(cog)

        def cmd_count(commands, depth: int = 0) -> int:
            count = 0

            if depth >= 10:
                log.warning("Max depth has been reached in the cog command count.")
                return 0

            for cmd in commands:
                if isinstance(cmd, discord.app_commands.Group):
                    count += cmd_count(cmd.commands, depth + 1)
                    continue
                count += 1
            return count

        commands_count = cmd_count(cog.get_app_commands())

        log.info(f"{commands_count} commands added from the cog {cog.qualified_name}.")

    async def setup_hook(self) -> None:
        await CogManager.load_cogs(self)
        commands = await self.tree.sync()
        log.info(f"{len(commands)} commands synced.")
        # await self.create_new_lavalink_node()

        await super().setup_hook()

    async def set_activity(self) -> None:
        await self.change_presence(
            activity=discord.Game(name=f"/help | v{__version__}")
        )

    async def create_lavalink_node(self) -> wavelink.Node:
        default_node = config.lavalink.get("default_node")
        node_uri = f"https://{default_node.get('host')}:{default_node.get('port')}"

        node = wavelink.Node(
            identifier=NODE_CODE_NAME.get_random(),
            uri=node_uri,
            password=default_node.get("pass"),
        )

        await wavelink.Pool.connect(nodes=[node], client=self, cache_capacity=100)
