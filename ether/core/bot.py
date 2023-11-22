
import discord
import wavelink
from discord import Intents
from discord.ext import commands

from ether import __version__
from ether.core.cog_manager import CogManager
from ether.core.config import config
from ether.core.constants import NODE_CODE_NAME
from ether.core.db.client import init_database
from ether.core.logging import log
from ether.core.tree import Tree


class Ether(commands.bot.AutoShardedBot):
    """The Ether subclass of discord.ext.commands.bot.AutoSharedBot"""

    def __init__(self, *, cli_flags=None, **kwargs) -> None:
        intents = Intents.all()
        super().__init__(
            command_prefix="", intents=intents, help_command=None, tree_cls=Tree, **kwargs
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

        commands_count = cmd_count(cog.walk_app_commands())

        log.info(f"{commands_count} commands added from the cog {cog.qualified_name}.")

    async def setup_hook(self) -> None:
        # Load cogs and sync commands
        await CogManager.load_cogs(self)
        commands = await self.tree.sync()
        log.info(f"{len(commands)} commands synced.")

        # Init database
        init_database(config.database.mongodb.get("uri"))

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
            password=default_node.get("pass")
        )

        await wavelink.Pool.connect(nodes=[node], client=self, cache_capacity=100)

    async def close(self) -> None:
        self.dispatch("close")

        await wavelink.Pool.close()
        await super().close()
