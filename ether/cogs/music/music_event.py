import discord

from discord.ext import commands
import wavelink

from ether.core.music import Player
from ether.core.constants import Colors
from ether.core.logging import log
from ether.core.utils import EtherEmbeds


class MusicEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        log.info(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: wavelink.Track):
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

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: Player, track: wavelink.Track, reason
    ):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """

        if reason not in ("FINISHED", "STOPPED", "REPLACED"):
            if player.text_channel:
                return await player.text_channel.send(
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
            vc: Player = member.guild.voice_client
            return await vc.disconnect()
