import datetime
import discord

import wavelink
from discord.ext import commands, tasks

from ether.core.constants import Links
from ether.core.logging import log
from ether.core.embed import Embed


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
        await self.client.create_lavalink_node()

        if len(wavelink.Pool.nodes) > 3:
            log.info("Removing a node...")
            older_node = None
            for node in wavelink.Pool.nodes:
                if not older_node:
                    older_node = node
                    continue
                if node.stats and node.stats.uptime < older_node.stats.uptime:
                    older_node = node

            await wavelink.Pool.remove_node(older_node, transfer_players=True)
            log.info(f"Node {older_node.label} removed")

    @tasks.loop(minutes=10)
    async def nodes_checkup(self):
        if not self.client.lavalink_ready_ran:
            return

        for node in wavelink.Pool.nodes:
            if not node.available:
                log.warning(f"An unavailable node has been found ({node.label})")
                await wavelink.Pool.remove_node(node, transfer_players=True)
                log.info(f"Node {node.label} removed")

                await self.client.start_lavalink_node()
                continue

            # Waking up nodes
            await node.fetch_route_planner_status()

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node):
        await wavelink.Pool.remove_node(node, transfer_players=True)
        log.warning(f"Node {node.label} was closed with dignity!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        player: wavelink.Player = payload.player
        track: wavelink.Playable = payload.track

        if hasattr(player, "message"):
            try:
                await player.message.delete()
                delattr(player, "message")
            except discord.errors.NotFound:
                pass

        if not hasattr(player, "current"):
            # Used because something weird appears sometimes
            log.error(f"Player ({type(player)}) has no attribute current track !")

        if hasattr(player, "text_channel") and player.text_channel:
            try:
                channel = player.text_channel

                td = datetime.timedelta(milliseconds=track.length)
                length = format_td(td)

                range_pointer_pos = min(int((60000 / track.length) * 30), 30)

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
                embed.set_footer(text=f"{player.node.label} ({player.node.host})")

                message: discord.Message = await channel.send(embed=embed)
                setattr(player, "message", message)
            except discord.errors.Forbidden:
                return

    @commands.Cog.listener()
    async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """
        player: wavelink.Player = payload.player
        reason = payload.reason

        reason = payload.reason
        player = payload.player

        if reason not in ("replaced", "finished"):
            if hasattr(player, "text_channel"):
                channel = player.text_channel
                error_message = f"Track finished for reason `{reason}` with node `{player.node.label}`({player.node.host}:{player.node.port})"

                if reason == "loadFailed":
                    error_message = f"Failed to load track probably due to the source. This error occured on the node `{player.node.label}`({player.node.host}:{player.node.port})"

                log.warn(error_message)

                try:
                    await channel.send(
                        embed=Embed.error(
                            error_message
                            + "\nIf the source is YouTube, try an other source beacause YouTube is blocking some videos"
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

        if player.loop:
            await player.play(player.current)
        elif player.queue and not reason == "REPLACED":
            await player.play(player.queue.pop(0))

    @commands.Cog.listener()
    async def on_wavelink_player_update(
        self, payload: wavelink.PlayerUpdateEventPayload
    ):
        player = payload.player

        if not player.current:
            await player.disconnect()

        if not hasattr(player, "message"):
            return

        message: discord.Message = player.message
        if not message:
            return

        embed = message.embeds[0]

        length = format_td(datetime.timedelta(milliseconds=player.current.length))

        min_max_pos = max(min(player.position, player.current.length), 0)
        position = format_td(datetime.timedelta(milliseconds=min_max_pos))
        pointer_pos = int((min_max_pos / player.current.length) * 30)

        range_pos = max(
            min(player.position + 60000, player.current.length), min_max_pos
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
