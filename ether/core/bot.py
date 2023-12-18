
import aiohttp
import discord
import wavelink
from discord import Intents
from discord.ext import commands

from ether import __version__
from ether.core.cog_manager import CogManager
from ether.core.config import config
from ether.core.constants import NODE_CODE_NAME
from ether.core.db.client import Database, init_database
from ether.core.logging import log
from ether.core.tree import Tree


class Ether(commands.bot.AutoShardedBot):
    """The Æther subclass of discord.ext.commands.bot.AutoSharedBot"""

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
        # Init database
        await init_database(config.database.mongodb.get("uri"))

        node_sessions = await Database.LavalinkNodeSessions.get_or_none(self.user.id)
        if node_sessions and len(node_sessions.sessions) > 0:
            for session_id in node_sessions.sessions:
                await self.create_lavalink_node(session_id=session_id)

        # Load cogs and sync commands
        await CogManager.load_cogs(self)
        commands = await self.tree.sync()
        log.info(f"{len(commands)} commands synced.")

        await super().setup_hook()

    async def set_activity(self) -> None:
        await self.change_presence(
            activity=discord.Game(name=f"/help | v{__version__}")
        )

    async def create_lavalink_node(self, session_id: str | None = None) -> wavelink.Node:
        default_node = config.lavalink.get("default_node")
        node_uri = f"https://{default_node.get('host')}:{default_node.get('port')}"

        identifiers = [n.identifier for n in wavelink.Pool.nodes]

        node = wavelink.Node(
            identifier=NODE_CODE_NAME.get_random(identifiers),
            uri=node_uri,
            password=default_node.get("pass")
        )

        if session_id:
            node._session_id = session_id

        await wavelink.Pool.connect(nodes=[node], client=self, cache_capacity=100)

        await self.save_lavalink_sessions()

    async def save_lavalink_sessions(self):
        log.debug("Saving session ids of lavalink nodes")

        sessions_id = []
        for identifier in wavelink.Pool.nodes:
            s_id = wavelink.Pool.get_node(identifier).session_id
            if s_id is None:
                continue

            sessions_id.append(s_id)


        await Database.LavalinkNodeSessions.register(
            bot_id=self.user.id,
            sessions=sessions_id
        )


    async def close(self) -> None:
        self.dispatch("close")

        await self.save_lavalink_sessions()

        await super().close()
