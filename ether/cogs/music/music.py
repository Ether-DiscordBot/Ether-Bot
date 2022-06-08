import datetime
import re
from typing import Optional
import random

import discord
from discord.ext import commands
from discord import Embed, Interaction, SlashCommandGroup
import pycord.wavelink as wavelink
from pycord.wavelink.tracks import YouTubeTrack, YouTubePlaylist
import humanize

from ether.core.constants import Colors
from ether.core.lavalink_status import request
from ether.core.logging import log
from ether.core.utils import EtherEmbeds

URL_REG = re.compile(r"https?://(?:www\.)?.+")


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

        await wavelink.NodePool.create_node(
            bot=self.client,
            host=f"{self.client.lavalink_host}",
            port=2333,
            password="pxV58RF6f292N9NK",
        )
    
    music = SlashCommandGroup("music", "Music commands!")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        log.info(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: wavelink.Track):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message are saved in the player.
        """
        channel = player.text_channel

        message: discord.Message = await channel.send(
            embed=Embed(
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

        if reason not in ("FINISHED", "STOPPED"):
            return await player.text_channel.send(embed=EtherEmbeds.error(f"Track finished for reason `{reason}`"))

        if not player.queue.is_empty:
            await player.play(player.queue.get())
        await player.message.delete()

    @music.command(name="join")
    async def _connect(self, interaction: Interaction) -> Optional[Player]:
        """
        This function can return None.

        The function/command to connect the bot to a voice channel.
        This function also create a wavelink queue for the tracks store in the voice client.
        """

        if not interaction.author.voice:
            await interaction.send_error("Please join a channel.")
            return None
        channel = interaction.author.voice.channel

        if not interaction.voice_client:
            player = Player(text_channel=interaction.channel)
            vc: Player = await interaction.user.voice.channel.connect(cls=player)
            vc.queue = wavelink.Queue(max_size=100)
            vc.text_channel = interaction.channel
            await interaction.guild.change_voice_state(
                channel=channel, self_mute=False, self_deaf=True
            )

            if interaction.command.qualified_name == "music join":
                await interaction.response.send_message(embed=Embed(description=f"`{interaction.author.voice.channel}` joined"))
        else:
            vc: Player = interaction.guild.voice_client

        return vc

    @music.command(name="leave")
    async def _disconnect(self, interaction: Interaction):
        """The function/command to leave a voice channel."""

        vc: Player = await self._connect(interaction)

        # Check if the voice client channel is the same as the user's voice channel.
        if vc.channel.id == vc.channel.id:
            await vc.disconnect()

            await interaction.response.send_message(embed=Embed(description=f"`{interaction.author.voice.channel}` leave"))
            return vc
    
    @music.command(name="search")
    async def search(self, interaction: Interaction, *, search: wavelink.YouTubeTrack):
        print(search)

    @music.command(name="play")
    async def _play(self, interaction: Interaction, *, query: str):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        if interaction.user.voice.channel.id != vc.channel.id and vc.is_playing:
            return await interaction.response.send_message(embed=EtherEmbeds.error("I'm already playing music in an other channel."), delete_after=5)
        
        print(query)

        track = await vc.node.get_tracks(cls=wavelink.YouTubeTrack, query=f'ytsearch:{query}')
        if not track:
            if not re.match(URL_REG, query):
                return await interaction.response.send_message(embed=EtherEmbeds.error("Could not find any songs with that query."), delete_after=5)
            track = await wavelink.YouTubeTrack.search(query)

        if isinstance(track, YouTubePlaylist):
            for t in track.tracks:
                vc.queue.put(t)

            await interaction.send(
                embed=Embed(
                    description=f"**[{len(track.tracks)} tracks]** added to queue!",
                    color=Colors.DEFAULT,
                )
            )
        elif isinstance(track, YouTubeTrack):
            vc.queue.put(track)

            await interaction.send(
                embed=Embed(
                    description=f"Track added to queue: **[{track.title}]({track.uri})**",
                    color=Colors.DEFAULT,
                )
            )

        if not vc.is_playing():
            track = vc.queue.get()
            await vc.play(track)

    @music.command(name="stop")
    async def _stop(self, interaction: Interaction):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        vc.queue.clear()
        await vc.stop()

        await interaction.response.send_message(embed=Embed(description="🛑 Stopped"), delete_after=5)

    @music.command(name="pause")
    async def pause(self, interaction: Interaction):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        if not vc.is_playing:
            await interaction.response.send_message(embed=EtherEmbeds.error("I am not currently playing anything!"), delete_after=5)
            return

        await vc.set_pause(not vc.is_paused())
        action = "▶️ Paused" if vc.is_paused() else "⏸️ Resume"
        await interaction.response.send_message(embed=Embed(description=action), delete_after=5)


    @music.command(name="resume")
    async def resume(self, interaction: Interaction):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        if not vc.is_paused():
            await interaction.response.send_message(embed=EtherEmbeds.error("I am not paused!"), delete_after=5)
            return

        await vc.set_pause(False)
        await interaction.response.send_message(embed=Embed(description="⏸️ Resume"), delete_after=5)


    @music.command(name="skip")
    async def _skip(self, interaction: Interaction):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        if vc.queue.is_empty:
            return

        await vc.play(vc.queue.get(), replace=True)
        await interaction.message.add_reaction("⏭️")
        return

    @music.command(name="shuffle")
    async def _shuffle(self, interaction: Interaction):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        shuffled_queue = vc.queue.copy()
        shuffled_queue = list(shuffled_queue)
        random.shuffle(shuffled_queue)
        vc.queue.clear()

        for tracks in shuffled_queue:
            vc.queue.put(tracks)

        await interaction.response.send_message(
            embed=Embed(
                description="The queue has been shuffled!", color=Colors.DEFAULT
            ),
            delete_after=10,
        )
        return vc.queue

    @music.command(name="queue")
    async def queue(self, interaction: Interaction):
        vc: Player = await self._connect(interaction)

        if not vc:
            return

        queue = vc.queue.copy()

        first_track = queue.get()
        embed = Embed(title=":notes: Queue:")
        embed.add_field(
            name="Now Playing:",
            value=f"`1.` [{first_track.title}]({first_track.uri[:30]}) | "
            f'`{datetime.timedelta(seconds=first_track.length) if not first_track.is_stream() else "🔴 Stream"}`',
            inline=False,
        )

        next_track_label = []
        for _ in range(10):
            if queue.is_empty:
                break
            track = queue.get()
            title = track.title
            if len(track.title) > 35:
                title = f"{title[:32]} ..."
            next_track_label.append(
                f"`{vc.queue.find_position(track) + 2}.` [{title}]({track.uri}) | "
                f"`{'🔴 Stream' if track.is_stream() else datetime.timedelta(seconds=track.length)}`"
            )

        if next_track_label:
            embed.add_field(
                name="Next 10 Tracks:", value="\n".join(next_track_label), inline=False
            )

        await interaction.response.send_message(embed=embed)

        return

    @music.command(name="lavalinkinfo")
    @commands.is_owner()
    async def lavalink_info(self, interaction: Interaction):
        player = interaction.guild.voice_client
        if not player: return 
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        embed = Embed(
            title=f"**WaveLink:** `{wavelink.__version__}`", color=Colors.DEFAULT
        )

        embed.add_field(
            name="Server",
            value=f"Server Memory: `{used}/{total}` | `({free} free)`\n"
            f"Server CPU: `{cpu}`\n"
            f"Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`",
            inline=False,
        )

        await interaction.response.send_message(embed=embed)
