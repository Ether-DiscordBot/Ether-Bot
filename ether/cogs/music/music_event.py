import discord

from discord.ext import commands
import mafic

from ether.core.constants import Colors
from ether.core.logging import log
from ether.core.utils import EtherEmbeds
from ether.core.voice_client import EtherPlayer


class MusicEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_track_start(self, event: mafic.TrackStartEvent[EtherPlayer]):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        if channel := event.player.channel:
            track = event.track
            channel = self.client.get_channel(channel)
            if not channel:
                return

            message: discord.Message = await channel.send(
                embed=discord.Embed(
                    description=f"Now Playing **[{track.title}]({track.uri})**!",
                    color=Colors.DEFAULT,
                )
            )
            setattr(event.player, "message", message)

    @commands.Cog.listener()
    async def on_track_end(self, event: mafic.TrackEndEvent[EtherPlayer]):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """

        reason = event.reason
        player = event.player

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

        if player.queue:
            await player.play(player.queue.pop(0))

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
            player: EtherPlayer = member.guild.voice_client
            return await player.stop()
