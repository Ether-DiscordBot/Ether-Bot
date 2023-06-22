import discord

from discord.ext import commands
import lavalink
from lavalink import NodeConnectedEvent, TrackStartEvent, TrackEndEvent

from ether.core.constants import Colors
from ether.core.logging import log
from ether.core.utils import EtherEmbeds
from ether.core.voice_client import EtherPlayer


class MusicEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_track_start(self, event: TrackStartEvent):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        player: EtherPlayer = event.player
        track = event.track

        if channel := player.text_channel:
            try:
                message: discord.Message = await channel.send(
                    embed=discord.Embed(
                        description=f"Now Playing **[{track.title}]({track.uri})**!",
                        color=Colors.DEFAULT,
                    )
                )
                setattr(player, "message", message)
            except discord.errors.Forbidden:
                return

    @commands.Cog.listener()
    async def on_track_end(self, event: TrackEndEvent):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """
        player: EtherPlayer = event.player
        reason = event.reason

        if reason not in ("FINISHED", "STOPPED", "REPLACED"):
            if channel := player.text_channel:
                try:
                    return await channel.send(
                        embed=EtherEmbeds.error(f"Track finished for reason `{reason}`")
                    )
                except discord.errors.Forbidden:
                    return

            log.warn(f"Track finished for reason `{reason}`")

        if not player.queue.is_empty and reason != "REPLACED":
            await player.play(player.queue.get())

        if hasattr(player, "message"):
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
