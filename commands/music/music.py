import discord
from discord.ext import commands
from discord import Embed
import wavelink
import re
import asyncio
import os

from core.util import colour
from core.util.colour import Colour

URL_REG = re.compile(r'https?://(?:www\.)?.+')


class Track(wavelink.Track):

    __slots__ = ('requester', 'channel_id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester') or None
        self.channel_id = kwargs.get('channel_id') or None

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
                                              identifier='client',
                                              region='us_central')

    
    @wavelink.WavelinkMixin.listener()
    async def on_track_start(self, node: wavelink.Node, payload):
        print(payload.player.queue.qsize())
        track = payload.player.queue._queue

        print(track[0])


    @wavelink.WavelinkMixin.listener()
    async def on_track_end(self, node: wavelink.Node, payload):
        if not payload.player.queue.empty():
            payload.player.queue.task_done()
            await payload.player.play(await payload.player.queue.get())


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
                return await ctx.send(embed=Embed(description='Could not find any songs with that query.', colour=Colour.ERROR), delete_after=15)
        else:
            tracks = await self.client.wavelink.get_tracks(query)
            if not tracks:    
                return await ctx.send(embed=Embed(description='Invalid URL.', colour=Colour.ERROR), delete_after=15)

        if not player.is_connected:
            await ctx.invoke(self.connect_)
        
        track = Track(tracks[0].id, tracks[0].info, requester=ctx.author, channel_id=ctx.channel.id)
        
        await player.queue.put(track)
        if not player.is_playing:
            track = player.queue.get_nowait()
            await player.play(track)
            print(track.channel_id)
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
                return await ctx.send(embed=Embed(description='I am not currently playing anything!', colour=Colour.ERROR), delete_after=15)

            await ctx.send(embed=Embed(description='Pausing the song!', colour=Colour.DEFAULT), delete_after=15)
            await player.set_pause(True)
        return

    @commands.command()
    async def resume(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            if not player.paused:
                return await ctx.send(embed=Embed(description='I am not currently paused!', colour=Colour.ERROR), delete_after=15)

            await ctx.send(embed=Embed(description='Resuming the player!', colour=Colour.DEFAULT), delete_after=15)
            return await player.set_pause(False)

        return
    
    @commands.command()
    async def loop(self, ctx):
        player = self.client.wavelink.get_player(ctx.guild.id)
        if ctx.author.voice and ctx.author.voice.channel.id == player.channel_id:
            player.queue._loop = not player.queue._loop
            if player.queue._loop:
                return await ctx.send(embed=Embed(description='Queue is looping!', colour=Colour.DEFAULT), delete_after=15)
            return await ctx.send(embed=Embed(description='Queue is no longer looping!', colour=Colour.DEFAULT), delete_after=15)

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
  
        #To Do




    """@commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def queue(self, ctx):
        queue = self.client.musicCmd.get_queue(ctx)

        if ctx.author.voice and ctx.author.voice.channel:
            is_in_client_channel = await self.client.musicCmd.user_is_in_client_channel(
                ctx
            )
            if is_in_client_channel:
                music_client = self.client.musicCmd.get_client(ctx.guild.id)
                if music_client.current is None and queue is None:
                    return
                if music_client.current is not None:
                    message = "# Current track: \n" "1.  {0.title} [{1}]\n".format(
                        music_client.current,
                        lavalink.utils.format_time(music_client.current.length),
                    )
                    if len(queue) > 0:
                        message += "\n# Queue: \n"
                        index = 1
                        for track in queue:
                            index += 1
                            if index == 10:
                                if len(queue) > 10:
                                    message += "{0}. {1.title} [{2}]\n...".format(
                                        index,
                                        track,
                                        lavalink.utils.format_time(track.length),
                                    )
                                else:
                                    message += "{0}. {1.title} [{2}]\n".format(
                                        index,
                                        track,
                                        lavalink.utils.format_time(track.length),
                                    )
                                break
                            message += "{0}.  {1.title} [{2}]\n".format(
                                index,
                                track,
                                lavalink.utils.format_time(track.length),
                            )

                    return await ctx.send(f"```glsl\n {message}```")
            else:
                embed = Embed(
                    description="You must be connected in the same voice channel as the bot."
                )
                return await ctx.send(embed=embed)
        else:
            embed = Embed(description="You must be connected to a voice channel.")
            return await ctx.send(embed=embed)"""
