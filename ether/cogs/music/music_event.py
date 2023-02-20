import discord

from discord.ext import commands
import lavalink
from lavalink import NodeConnectedEvent, TrackStartEvent, TrackEndEvent

from ether.core.constants import Colors
from ether.core.logging import log
from ether.core.utils import EtherEmbeds


class MusicEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @lavalink.listener(NodeConnectedEvent)
    async def on_node_connnected(self, node: lavalink.Node):
        """Event fired when a node has finished connecting."""
        log.info(f"Node: <{node.identifier}> is ready!")

    @lavalink.listener(TrackStartEvent)
    async def on_wavelink_track_start(self, player, track):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        if channel := player.text_channel:
            message: discord.Message = await channel.send(
                embed=discord.Embed(
                    description=f"Now Playing **[{track.title}]({track.uri})**!",
                    color=Colors.DEFAULT,
                )
            )
            player.message = message

    @lavalink.listener(TrackEndEvent)
    async def on_wavelink_track_end(self, player, track, reason):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """

        if reason not in ("FINISHED", "STOPPED", "REPLACED"):
            if player.channel_id:
                channel = self.client.get_guild(player.guild_id).get_channel(
                    player.channel_id
                )
                if channel:
                    return await channel.send(
                        embed=EtherEmbeds.error(f"Track finished for reason `{reason}`")
                    )

            log.warn(f"Track finished for reason `{reason}`")

        if not player.queue.is_empty and reason != "REPLACED":
            await player.play(player.queue.get())

        if player.message:
            await player.message.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (  # Check if the bot was move to an empty channel
            member.id == self.client.user.id
            and after.channel
            and len(after.channel.members) <= 1
        ) or (  # Check is nobody is in the channel
            not member.bot
            and member.guild.me.voice
            and (before.channel.id == member.guild.me.voice.channel.id)
            and len(before.channel.members) <= 1
        ):
            player = self.client.lavalink.player_manager.get(member.guild.id)
            return await player.stop()
