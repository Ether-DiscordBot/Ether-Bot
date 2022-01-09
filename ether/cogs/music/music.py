from inspect import Traceback
import discord
from discord.ext import commands
from discord import Embed
import wavelink
import re
import asyncio
import random
from wavelink.player import TrackPlaylist
from aiohttp import ClientConnectionError
import humanize
import datetime

from ether import Color


URL_REG = re.compile(r'https?://(?:www\.)?.+')


class Track(wavelink.Track):

    __slots__ = ('requester', 'channel_id', 'message')

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester') or None
        self.channel_id = kwargs.get('channel_id') or None
        self.message = None

class Music(commands.Cog, wavelink.WavelinkMixin, name="music"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Music"

        if not hasattr(client, 'wavelink'):
            self.client.wavelink = wavelink.Client(bot=self.client)

        self.client.loop.create_task(self.start_nodes())
    

    async def start_nodes(self):
        await self.client.wait_until_ready()

        await self.client.wavelink.initiate_node(
            host=f'{self.client.lavalink_host}',
            port=2333,
            rest_uri=f'http://{self.client.lavalink_host}:2333',
            password="pxV58RF6f292N9NK",
            identifier='ETHER GLOBAL',
            region='us_central'
        )

    @wavelink.WavelinkMixin.listener()
    async def on_track_start(self, node: wavelink.Node, payload):
        """When a track starts, the bot sends a message in the channel where the command was sent.
        The channel is taken on the object of the track and the message is saved in the player.
        """
        
        track = payload.player.current
        channel = self.client.get_channel(track.channel_id)

        payload.player.message = await channel.send(embed=Embed(
            description=f"Now Playing **[{track.title}]({track.uri})**!",
            color=Color.DEFAULT
            ))
        

    @wavelink.WavelinkMixin.listener()
    async def on_track_end(self, node: wavelink.Node, payload:wavelink.events.TrackEnd):
        """When a track ends, the bot delete the start message.
        If it's the last track, the player is kill.
        """
        
        if not payload.player.queue.empty():
            payload.player.queue.task_done()
            await payload.player.play(await payload.player.queue.get())
        await payload.player.message.delete()


    @commands.command(name="join")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _connect(self, ctx, *, channel: discord.VoiceChannel=None):
        """The function/command to connect the bot to a voice channel.
        This function also create an asyncio queue used as a queue for the tracks.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send(embed=Embed(description="Please join a channel.", color=Color.ERROR))

        
        player = self.client.wavelink.get_player(ctx.guild.id)
        player.queue = asyncio.Queue(maxsize=100)
        await player.connect(channel.id)
        
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

        await ctx.message.add_reaction("👌")
        return player


    @commands.command(name="leave")
    async def _disconnect(self, ctx, *, channel: discord.VoiceChannel=None):
        """The function/command to leave a voice channel.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send(embed=Embed(description="You must be connected on a voice channel.", color=Color.ERROR))
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        if player.channel_id == channel.id:
            await player.disconnect()

            await ctx.message.add_reaction("👋")
            return player

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send(embed=Embed(description="You must be connected on a voice channel.", color=Color.ERROR))

        player = self.client.wavelink.get_player(ctx.guild.id)

        if ctx.author.voice.channel.id != player.channel_id:
            if player.is_playing:
                return await ctx.send(embed=Embed(description="I'm already playing music in an other channel.", color=Color.ERROR))
            
            await ctx.invoke(self._connect)
        
        if not bool(player.node):
            player.change_node()
        
        if not URL_REG.match(query):            
            tracks = await self.client.wavelink.get_tracks(f'ytsearch:{query}')
            if not tracks:
                return await ctx.send(embed=Embed(description='Could not find any songs with that query.', color=Color.ERROR), delete_after=10)
        else:
            tracks = await self.client.wavelink.get_tracks(query)
            if not tracks:    
                return await ctx.send(embed=Embed(description='Invalid URL.', color=Color.ERROR), delete_after=10)

        if not player.is_connected:
            await ctx.invoke(self._connect)

        if isinstance(tracks, TrackPlaylist):
            for t in tracks.tracks:
                track = Track(t.id, t.info, requester=ctx.author, channel_id=ctx.channel.id)
                await player.queue.put(track)
            await ctx.send(embed=Embed(description=f"**[{len(tracks.tracks)} tracks]({query})** added to queue!", color=Color.DEFAULT))
        else:
            track = Track(tracks[0].id, tracks[0].info, requester=ctx.author, channel_id=ctx.channel.id)
            await player.queue.put(track)

        if not player.is_playing:
            track = player.queue.get_nowait()
            await player.play(track)
        else:
            if isinstance(tracks, TrackPlaylist):
                return tracks.tracks
            
            await ctx.send(embed=Embed(description=f"Track added to queue: **[{track.title}]({track.uri})**", color=Color.DEFAULT))
            return track

    @commands.command(name="stop")
    async def _stop(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        if player.channel_id == channel.id:
            while player.queue.qsize() > 0:
                await player.queue.get()
                player.queue.task_done()
            await player.stop()

            await ctx.message.add_reaction("🛑")
            return player

    @commands.command()
    async def pause(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            if not player.is_playing:
                return await ctx.send(embed=Embed(description='I am not currently playing anything!', color=Color.ERROR), delete_after=10)

            await ctx.send(embed=Embed(description='Pausing the song!', color=Color.DEFAULT), delete_after=10)
            await player.set_pause(True)
        return

    @commands.command()
    async def resume(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            if not player.paused:
                return await ctx.send(embed=Embed(description='I am not currently paused!', color=Color.ERROR), delete_after=10)

            await ctx.send(embed=Embed(description='Resuming the player!', color=Color.DEFAULT), delete_after=10)
            return await player.set_pause(False)

        return
    
    @commands.command()
    async def loop(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            player.queue._loop = not player.queue._loop
            if player.queue._loop:
                return await ctx.send(embed=Embed(description='Queue is looping!', color=Color.DEFAULT), delete_after=10)
            return await ctx.send(embed=Embed(description='Queue is no longer looping!', color=Color.DEFAULT), delete_after=10)

        return
  
    @commands.command(name="skip")
    async def _skip(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        if player.channel_id == channel.id:
            await player.stop()

            await ctx.message.add_reaction("⏭️")
            return player

    
    @commands.command(name="shuffle")
    async def _shuffle(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        if player.channel_id == channel.id:
            random.shuffle(player.queue._queue)

            await ctx.send(embed=Embed(description='Queue has been shuffled!', color=Color.DEFAULT), delete_after=10)
            return player.queue._queue
    
  
    @commands.command(name="queue", aliases=["q", "list"])
    async def queue(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            embed = Embed(title=":notes: Queue:")
            embed.add_field(
                name="Now Playing:",
                value=f'`1.` [{player.current.title}]({player.current.uri[:30]}) | `{"🔴 Stream" if player.current.is_stream else datetime.timedelta(milliseconds=player.current.length)}`',
                inline=False,
            )


            next_track_label = []
            for track in player.queue._queue:
                if track != player.current and player.queue._queue.index(track) < 10:
                    title = track.title
                    if len(track.title) > 35:
                        title = title[:32] + " ..."
                    next_track_label.append(f"`{player.queue._queue.index(track)+2}.` [{title}]({track.uri}) | `{'🔴 Stream' if track.is_stream else datetime.timedelta(milliseconds=track.length)}`"),

            if next_track_label:
                embed.add_field(
                    name="Next 10 Tracks:",
                    value="\n".join(next_track_label),
                    inline=False
                )

            await ctx.send(embed=embed)

        return

    @commands.command(name="remove", aliases=["rm"])
    async def remove(self, ctx, *, index: int):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            if index > len(player.queue._queue)+1 or index <= 1:
                return await ctx.send(embed=Embed(description="Index out of range.", color=Color.ERROR))
            player.queue._queue.__delitem__(index-2)
            await ctx.message.add_reaction("👌")

    @commands.command(name="lavalinkinfo")
    async def lavalink_info(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        embed = Embed(title=f'**WaveLink:** `{wavelink.__version__}`', color=Color.DEFAULT)

        embed.add_field(name="Node", value=f'Connected to `{len(self.client.wavelink.nodes)}` nodes.\n' \
            f'Best available Node `{self.client.wavelink.get_best_node().__repr__()}`\n' \
            f'`{len(self.client.wavelink.players)}` players are distributed on nodes.\n' \
            f'`{node.stats.players}` players are distributed on server.\n' \
            f'`{node.stats.playing_players}` players are playing on server.')
        
        embed.add_field(name="Server", value=f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
            f'Server CPU: `{cpu}`\n' \
            f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`',
            inline=False)

        await ctx.send(embed=embed)