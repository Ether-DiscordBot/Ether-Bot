import datetime
import discord

from discord.ext import commands
import humanize
import mafic

from ether.core.constants import Links
from ether.core.logging import log
from ether.core.utils import EtherEmbeds
from ether.core.voice_client import EtherPlayer


def format_td(td):
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60

    return (
        f"{hours:02}:{minutes:02}:{seconds:02}"
        if hours
        else f"{minutes:02}:{seconds:02}"
    )


class MusicEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_track_start(self, event: mafic.TrackStartEvent):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        player: EtherPlayer = event.player
        track: mafic.Track = event.track

        if channel := player.text_channel:
            try:
                td = datetime.timedelta(milliseconds=track.length)
                length = format_td(td)
                embed = discord.Embed(
                    title=track.title,
                    url=track.uri,
                    description=f"`00:00` █───────────────────────────── `{length}`",
                )
                embed.set_thumbnail(
                    url=f"http://i.ytimg.com/vi/{track.identifier}/mqdefault.jpg"
                )
                embed.set_author(name=track.author, icon_url=Links.VINYL_GIF_URL)

                message: discord.Message = await channel.send(embed=embed)
                setattr(player, "message", message)
            except discord.errors.Forbidden:
                return

    @commands.Cog.listener()
    async def on_track_end(self, event: mafic.TrackEndEvent):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """
        player: EtherPlayer = event.player
        reason = event.reason

        reason = event.reason
        player = event.player

        if reason not in ("FINISHED", "STOPPED", "REPLACED"):
            if channel := player.text_channel:
                try:
                    return await channel.send(
                        embed=EtherEmbeds.error(f"Track finished for reason `{reason}`")
                    )
                except discord.errors.Forbidden:
                    return

            log.warn(f"Track finished for reason `{reason}`")

        if player.queue and not reason == "REPLACED":
            await player.play(player.queue.pop(0))
        elif not player.queue:
            await player.disconnect()

        if hasattr(player, "message"):
            await player.message.delete()

    @commands.Cog.listener()
    async def on_node_stats(self, node: mafic.Node):
        for player in node.players:
            if player.current is None:
                await player.disconnect()

            if not hasattr(player, "message"):
                continue
            message: discord.Message = player.message
            if not message:
                continue

            embed = message.embeds[0]

            length = format_td(datetime.timedelta(milliseconds=player.current.length))
            min_max_pos = max(min(player.position, player.current.length), 0)
            position = format_td(datetime.timedelta(milliseconds=min_max_pos))

            pointer_pos = int((player.position / player.current.length) * 30)

            description = f"`{position}` {'─' * (pointer_pos-1)}█{'─' * (30-pointer_pos)} `{length}`"
            embed.description = description
            message = await message.edit(embed=embed)
            setattr(player, "message", message)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (  # Check if the bot was move to an empty channel
            member.id == self.client.user.id
            and after.channel
            and len(after.channel.members) <= 1
        ) or (  # Check is nobody is in the channel
            before
            and before.channel
            and not member.bot
            and member.guild.me.voice
            and (before.channel.id == member.guild.me.voice.channel.id)
            and len(before.channel.members) <= 1
        ):
            player: EtherPlayer = member.guild.voice_client
            return await player.stop()
