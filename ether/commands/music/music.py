import discord
from discord.ext import commands
from discord import Embed
import wavelink
import re
import asyncio
import os
import random
from wavelink.player import TrackPlaylist
import humanize
import datetime

from ether import Colour

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
    
        await self.client.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password="pxV58RF6f292N9NK",
                                              identifier='MAIN',
                                              region='us_central')

    
    @wavelink.WavelinkMixin.listener()
    async def on_track_start(self, node: wavelink.Node, payload):
        track = payload.player.current
        channel = self.client.get_channel(track.channel_id)

        payload.player.message = await channel.send(embed=Embed(description=f"Now Playing **[{track.title}]({track.uri})**!", colour=Colour.DEFAULT))
        

    @wavelink.WavelinkMixin.listener()
    async def on_track_end(self, node: wavelink.Node, payload:wavelink.events.TrackEnd):
        if not payload.player.queue.empty():
            payload.player.queue.task_done()
            await payload.player.play(await payload.player.queue.get())
        await payload.player.message.delete()


    @commands.command(name="join")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _connect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return ctx.send(embed=Embed(description="Please join a channel.", colour=Colour.ERROR))

        player = self.client.wavelink.get_player(ctx.guild.id)
        player.queue = asyncio.Queue(maxsize=100, loop=False)
        await player.connect(channel.id)

        await ctx.message.add_reaction("👌")
        return player


    @commands.command(name="leave")
    async def _disconnect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send(embed=Embed(description="You must be connected on a voice channel.", colour=Colour.ERROR))
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        if player.channel_id == channel.id:
            await player.disconnect()

            await ctx.message.add_reaction("👋")
            return player


    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send(embed=Embed(description="You must be connected on a voice channel.", colour=Colour.ERROR))

        player = self.client.wavelink.get_player(ctx.guild.id)

        if ctx.author.voice.channel.id != player.channel_id:
            if player.is_playing:
                return await ctx.send(embed=Embed(description="I'm already playing music in an other channel.", colour=Colour.ERROR))
            
            await ctx.invoke(self._connect)
        
        if not URL_REG.match(query):            
            tracks = await self.client.wavelink.get_tracks(f'ytsearch:{query}')
            if not tracks:
                return await ctx.send(embed=Embed(description='Could not find any songs with that query.', colour=Colour.ERROR), delete_after=10)
        else:
            tracks = await self.client.wavelink.get_tracks(query)
            if not tracks:    
                return await ctx.send(embed=Embed(description='Invalid URL.', colour=Colour.ERROR), delete_after=10)

        if not player.is_connected:
            await ctx.invoke(self.connect_)

        if isinstance(tracks, TrackPlaylist):
            for t in tracks.tracks:
                track = Track(t.id, t.info, requester=ctx.author, channel_id=ctx.channel.id)
                await player.queue.put(track)
            await ctx.send(embed=Embed(description=f"**[{len(tracks.tracks)} tracks]({query})** added to queue!", colour=Colour.DEFAULT))
        else:
            track = Track(tracks[0].id, tracks[0].info, requester=ctx.author, channel_id=ctx.channel.id)
            await player.queue.put(track)

        if not player.is_playing:
            track = player.queue.get_nowait()
            await player.play(track)
        else:
            if isinstance(tracks, TrackPlaylist):
                return tracks.tracks
            
            await ctx.send(embed=Embed(description=f"Track added to queue: **[{track.title}]({track.uri})**", colour=Colour.DEFAULT))
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
                return await ctx.send(embed=Embed(description='I am not currently playing anything!', colour=Colour.ERROR), delete_after=10)

            await ctx.send(embed=Embed(description='Pausing the song!', colour=Colour.DEFAULT), delete_after=10)
            await player.set_pause(True)
        return

    @commands.command()
    async def resume(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            if not player.paused:
                return await ctx.send(embed=Embed(description='I am not currently paused!', colour=Colour.ERROR), delete_after=10)

            await ctx.send(embed=Embed(description='Resuming the player!', colour=Colour.DEFAULT), delete_after=10)
            return await player.set_pause(False)

        return
    
    @commands.command()
    async def loop(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            player.queue._loop = not player.queue._loop
            if player.queue._loop:
                return await ctx.send(embed=Embed(description='Queue is looping!', colour=Colour.DEFAULT), delete_after=10)
            return await ctx.send(embed=Embed(description='Queue is no longer looping!', colour=Colour.DEFAULT), delete_after=10)

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

            await ctx.send(embed=Embed(description='Queue has been shuffled!', colour=Colour.DEFAULT), delete_after=10)
            return player.queue._queue
    
  
    @commands.command(name="queue", aliases=["q", "list"])
    async def queue(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            embed = Embed(title=":notes: Queue:")
            embed.add_field(
                name="Now Playing:",
                value=f"`1.` [{player.current.title}]({player.current.uri[0: 30]}) | `{datetime.timedelta(milliseconds=player.current.length)}`",
                inline=False
            )

            next_track_label = []
            for track in player.queue._queue:
                if track != player.current and player.queue._queue.index(track) < 10:
                    title = track.title
                    if len(track.title) > 35:
                        title = title[0: 32] + " ..."
                    next_track_label.append(f"`{player.queue._queue.index(track)+2}.` [{title}]({track.uri}) | `{datetime.timedelta(milliseconds=track.length)}`"),

            embed.add_field(
                name="Next 10 Tracks:",
                value="\n".join(next_track_label),
                inline=False
            )
            
            await ctx.send(embed=embed)
                
        return


    @commands.command(name="lavalinkinfo")
    async def info(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        embed = Embed(title=f'**WaveLink:** `{wavelink.__version__}`', colour=Colour.DEFAULT)

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