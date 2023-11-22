import asyncio
import datetime

import discord
import wavelink
from discord.ext import commands, tasks

from ether.core.constants import Links
from ether.core.embed import Embed
from ether.core.logging import log


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

        self.update_lavalink_nodes.start()

    @tasks.loop(hours=2)
    async def update_lavalink_nodes(self):
        if len(wavelink.Pool.nodes) < 3:
            await self.client.create_lavalink_node()

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list[wavelink.Player]):
        log.warning(f"Node {node.identifier} was closed with dignity!")

        for player in disconnected:
            if hasattr(player, "message"):
                try:
                    msg: discord.Message = player.message
                    await msg.delete()
                except:
                    pass

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        player: wavelink.Player | None = payload.player
        track: wavelink.Playable = payload.track

        if not player:
            # Handle edge cases...
            return


        if hasattr(player, "home") and player.home:
            try:
                channel = player.home

                td = datetime.timedelta(milliseconds=track.length)
                length = format_td(td)

                range_pointer_pos = min(int((500 / track.length) * 30), 30)

                range = ["─"] * 30
                range[:range_pointer_pos] = "░" * range_pointer_pos
                range[0] = "█"
                range = "".join(range)

                description = f"`00:00` {range} `{length}`"

                embed = discord.Embed(
                    title=track.title,
                    url=track.uri,
                    description=description,
                )
                embed.set_thumbnail(
                    url=f"http://i.ytimg.com/vi/{track.identifier}/mqdefault.jpg"
                )
                embed.set_author(name=track.author, icon_url=Links.VINYL_GIF_URL)
                embed.set_footer(text=f"{player.node.identifier}")

                message: discord.Message = await channel.send(embed=embed)
                setattr(player, "message", message)
            except discord.errors.Forbidden:
                return

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """
        player: wavelink.Player | None = payload.player
        reason = payload.reason

        if not player:
            log.warning(f"Track from an unknown Player stopped for the reason: {reason}")

        if reason not in ("replaced", "finished", "stopped"):
            if hasattr(player, "home"):
                channel = player.home
                error_message = f"Track finished for reason `{reason}` with node `{player.node.identifier}`"

                if reason == "loadFailed":
                    error_message = f"Failed to load track probably due to the source. This error occurred on the node `{player.node.identifier}`"

                log.warning(error_message)

                try:
                    await channel.send(
                        embed=Embed.error(
                            description=error_message
                            + "\nIf the source is YouTube, try an other source because YouTube is blocking some videos"
                        )
                    )
                except discord.errors.Forbidden:
                    pass

        if hasattr(player, "message"):
            try:
                await player.message.delete()
            except discord.errors.NotFound:
                pass
            delattr(player, "message")

    @commands.Cog.listener()
    async def on_wavelink_player_update(
        self, payload: wavelink.PlayerUpdateEventPayload
    ):
        player = payload.player

        if not player:
            return


        def check_player_usage() -> bool:
            return player and not player.playing and (len(player.queue) <= 0 or len(player.auto_queue) <= 0)

        # Ugly function
        if check_player_usage():
            # Let the player to be ready
            await asyncio.sleep(10.0)
            if check_player_usage():
                await player.disconnect()

        if not hasattr(player, "message"):
            return

        try:
            message: discord.Message = player.message
            if not message or not player.current:
                return

            await message.fetch()
            embed = message.embeds[0]

            length = format_td(datetime.timedelta(milliseconds=player.current.length))

            min_max_pos = max(min(player.position, player.current.length), 0)
            position = format_td(datetime.timedelta(milliseconds=min_max_pos))
            pointer_pos = int((min_max_pos / player.current.length) * 30)

            range_pos = max(
                min(player.position + 500, player.current.length), min_max_pos
            )
            range_pointer_pos = min(int((range_pos / player.current.length) * 30), 30)
            range = ["─"] * 30
            range[pointer_pos:range_pointer_pos] = "░" * (range_pointer_pos - pointer_pos)
            range[pointer_pos] = "█"
            range = "".join(range[:30])

            description = f"`{position}` {range} `{length}`"
            embed.description = description
            edited_message = await message.edit(embed=embed)
            setattr(player, "message", edited_message)
        except discord.errors.NotFound:
            return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, _before, _after):
        if member.guild.me.voice and len(member.guild.me.voice.channel.members) <= 1:
            player: wavelink.Player = member.guild.voice_client
            if not player:
                return

            await player.disconnect(force=True)

            if hasattr(player, "message"):
                try:
                    await player.message.delete()
                except discord.errors.NotFound:
                    pass
                delattr(player, "message")

        if not member.guild.me.voice and member.guild.voice_client:
            player: wavelink.Player = member.guild.voice_client
            if not player:
                return

            if hasattr(player, "message"):
                try:
                    await player.message.delete()
                except discord.errors.NotFound:
                    pass
                delattr(player, "message")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self, payload: wavelink.NodeReadyEventPayload
    ) -> None:
        node: wavelink.Node = payload.node

        log.info(f"Node {node.identifier} is ready")
