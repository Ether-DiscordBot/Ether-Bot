from core.util import colour
from core.util.colour import Colour
import os
import discord
from discord.ext import commands
from discord import Embed

import requests

import lavalink
import wavelink


class Music(commands.Cog, name="music"):
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
                                              identifier='TEST',
                                              region='us_central')


    @commands.command(name="join")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _connect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return ctx.send(embed=Embed(description="Please join a channel.", colour=Colour.ERROR))

        player = self.client.wavelink.get_player(ctx.guild.id)
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
        
        try:
            requests.get(query)
            tracks = await self.client.wavelink.get_tracks(query)
        except requests.ConnectionError as exception:
            return await ctx.send(embed=Embed(description='Invalid URL.', colour=Colour.ERROR), delete_after=15)
        except requests.exceptions.InvalidURL as exception:
            tracks = await self.client.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await ctx.send(embed=Embed(description='Could not find any songs with that query.', colour=Colour.ERROR), delete_after=15)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        await ctx.send(f'Added {str(tracks[0])} to the queue.')
        await player.play(tracks[0], replace=player.position == 0)


    @commands.command(name="stop")
    async def _stop(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        if player.channel_id == channel.id:
            await player.stop()

            await ctx.message.add_reaction("🛑")
            print(player.tracks)
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

