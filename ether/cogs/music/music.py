import logging
import datetime
import re
from typing import Optional
import random

import discord
from discord.ext import commands
from discord import Embed
import wavelink
from wavelink.tracks import YouTubeTrack, YouTubePlaylist
import humanize

import ether.core
from ether.core import Color, request

URL_REG = re.compile(r'https?://(?:www\.)?.+')

logger = logging.getLogger("ether_log")


class Player(wavelink.Player):
    def __init__(self, text_channel: discord.TextChannel):
        super().__init__()
        self.message: Optional[discord.Message] = None
        self.text_channel = text_channel
        self.queue: wavelink.Queue = wavelink.Queue(max_size=100)


class Music(commands.Cog, name="music"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Music"

        client.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.client.wait_until_ready()

        r = request()
        if r != 0:
            return

        await wavelink.NodePool.create_node(bot=self.client,
                                            host=f'{self.client.lavalink_host}',
                                            port=2333,
                                            password="pxV58RF6f292N9NK",
                                            )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        logger.debug(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: wavelink.Track):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        channel = player.text_channel

        message: discord.Message = await channel.send(embed=Embed(
            description=f"Now Playing **[{track.title}]({track.uri})**!",
            color=Color.DEFAULT
        ))
        player.message = message

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: wavelink.Track, reason):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """

        if reason not in ("FINISHED", "STOPPED"):
            return await player.text_channel.send(embed=Embed(description=f"Track finished for reason `{reason}`",
                                                              color=Color.ERROR))

        if not player.queue.is_empty:
            await player.play(player.queue.get())
        await player.message.delete()

    @commands.command(name="join")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _connect(self, ctx: ether.core.EtherContext) -> Optional[Player]:
        """
        This function can return None.

        The function/command to connect the bot to a voice channel.
        This function also create a wavelink queue for the tracks store in the voice client.
        """

        if not ctx.author.voice:
            await ctx.send_error("Please join a channel.")
            return None
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            player = Player(text_channel=ctx.channel)
            vc: Player = await ctx.author.voice.channel.connect(cls=player)
            vc.queue = wavelink.Queue(max_size=100)
            vc.text_channel = ctx.channel
            await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

            if ctx.command == "join":
                await ctx.message.add_reaction("👌")
        else:
            vc: Player = ctx.voice_client

        return vc

    @commands.command(name="leave")
    async def _disconnect(self, ctx):
        """The function/command to leave a voice channel.
        """

        vc: Player = await ctx.invoke(self._connect)

        # Check if the voice client channel is the same as the user's voice channel.
        if vc.channel.id == vc.channel.id:
            await vc.disconnect()

            await ctx.message.add_reaction("👋")
            return vc

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx: ether.core.EtherContext, *, query):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        if ctx.author.voice.channel.id != vc.channel.id and vc.is_playing:
            return await ctx.send_error("I'm already playing music in an other channel.")

        try:
            track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        except IndexError:
            if not re.match(URL_REG, query):
                return await ctx.send_error("Could not find any songs with that query.", delete_after=5)
            track = await vc.node.get_playlist(YouTubePlaylist, query)

        if isinstance(track, YouTubePlaylist):
            for t in track.tracks:
                vc.queue.put(t)

            await ctx.send(embed=Embed(description=f"**[{len(track.tracks)} tracks]** added to queue!",
                                       color=Color.DEFAULT))
        elif isinstance(track, YouTubeTrack):
            vc.queue.put(track)

            await ctx.send(embed=Embed(
                description=f"Track added to queue: **[{track.title}]({track.uri})**",
                color=Color.DEFAULT))

        if not vc.is_playing():
            track = vc.queue.get()
            await vc.play(track)

    @commands.command(name="stop")
    async def _stop(self, ctx):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        vc.queue.clear()
        await vc.stop()

        await ctx.message.add_reaction("🛑")

    @commands.command(name="pause")
    async def pause(self, ctx):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        if not vc.is_playing:
            await ctx.send_error("I am not currently playing anything!", delete_after=5)
            return

        await vc.set_pause(not vc.is_paused())
        reaction = "▶️" if vc.is_paused() else "⏸️"
        await ctx.message.add_reaction(reaction)

    @commands.command(name="resume")
    async def resume(self, ctx):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        if not vc.is_paused():
            await ctx.send_error("I am not paused!", delete_after=5)
            return

        await vc.set_pause(False)
        await ctx.message.add_reaction("▶️")

    @commands.command(name="skip")
    async def _skip(self, ctx):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        if vc.queue.is_empty:
            return

        await vc.play(vc.queue.get(), replace=True)
        await ctx.message.add_reaction("⏭️")
        return

    @commands.command(name="shuffle")
    async def _shuffle(self, ctx):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        shuffled_queue = vc.queue.copy()
        shuffled_queue = list(shuffled_queue)
        random.shuffle(shuffled_queue)
        vc.queue.clear()

        for tracks in shuffled_queue:
            vc.queue.put(tracks)

        await ctx.send(embed=Embed(description='The queue has been shuffled!', color=Color.DEFAULT), delete_after=10)
        return vc.queue

    @commands.command(name="queue", aliases=["q", "list"])
    async def queue(self, ctx):
        vc: Player = await ctx.invoke(self._connect)

        if not vc:
            return

        queue = vc.queue.copy()

        first_track = queue.get()
        embed = Embed(title=":notes: Queue:")
        embed.add_field(
            name="Now Playing:",
            value=f'`1.` [{first_track.title}]({first_track.uri[:30]}) | '
                  f'`{datetime.timedelta(seconds=first_track.length) if not first_track.is_stream() else "🔴 Stream"}`',
            inline=False
        )

        next_track_label = []
        for _ in range(10):
            if queue.is_empty:
                break
            track = queue.get()
            title = track.title
            if len(track.title) > 35:
                title = f'{title[:32]} ...'
            next_track_label.append(
                f"`{vc.queue.find_position(track) + 2}.` [{title}]({track.uri}) | "
                f"`{'🔴 Stream' if track.is_stream() else datetime.timedelta(seconds=track.length)}`")

        if next_track_label:
            embed.add_field(
                name="Next 10 Tracks:",
                value="\n".join(next_track_label),
                inline=False
            )

        await ctx.send(embed=embed)

        return

    @commands.is_owner()
    @commands.command(name="lavalinkinfo")
    async def lavalink_info(self, ctx):
        player = ctx.voice_client
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        embed = Embed(title=f'**WaveLink:** `{wavelink.__version__}`', color=Color.DEFAULT)

        embed.add_field(name="Server", value=f'Server Memory: `{used}/{total}` | `({free} free)`\n'
                                             f'Server CPU: `{cpu}`\n' 
                                             f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`',
                        inline=False)

        await ctx.send(embed=embed)
