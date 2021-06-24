import urllib.parse
import discord
import lavalink
import wavelink

from youtubesearchpython import VideosSearch
from core.util.lavalinkmanager import LavalinkManager

from discord import Embed

import os


class MusicCommandsManager:
    def __init__(self, client):
        self.client = client
    
        
        if not hasattr(client, 'wavelink'):
            self.client.wavelink = wavelink.Client(bot=self.client)

        self.client.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.client.wait_until_ready()

        await self.client.wavelink.initiate_node(host=os.getenv("LAVALINK_HOST"),
                                              port=os.getenv("LAVALINK_PORT"),
                                              rest_uri=os.getenv("LAVALINK_HOST"),
                                              password=os.getenv("LAVALINK_PASS"),
                                              identifier='MOCHI',
                                              region='eu')

        # await self.lavalink.initialize_lavalink()

    async def user_is_in_client_channel(self, ctx, try=5):
        client = self.client.wavelink.get_player(ctx.guild.id)

        if client is None:
            await self.join_voice_channel(ctx)
            if try > 0:
                return await self.user_is_in_client_channel(ctx, try=try-1)
            return False

        if client and client.channel_ids:
            if ctx.author.voice and ctx.author.voice.channel.id == client.channel_id:
                return True

        return False

    async def join_voice_channel(self, channel: discord.VoiceChannel=None):
        if channel:
            player = self.client.wavelink.get_player(channel.guild.id)
            return await player.connect(channel.id)

        return "You must be connected to a voice channel."

    async def play(self, ctx):
        """
        :param ctx: context
        :return: True or None
        """

        music_client = self.client.wavelink.get_player(ctx.guild.id)

        if music_client is None:
            music_client = await self.join_voice_channel(ctx)

        if music_client.current is None and music_client.channel:
            await music_client.play()
            return True
        return None

    async def next_track(self, ctx):
        """
        :param ctx: context
        :return: True or None
        """

        music_client = self.client.wavelink.get_player(ctx.guild.id)

        if music_client and music_client.channel:
            await music_client.skip()
            return True
        return None

    async def stop(self, ctx):
        """
        :param ctx: context
        :return: True or None
        """

        music_client = self.get_client(ctx.guild.id)

        if music_client and music_client.is_playing and music_client.channel:
            await music_client.current.start_message.delete()
            await music_client.stop()
            return True
        return None

    async def pause(self, ctx, pause):
        """
        :param ctx: context
        :return: True or None
        """
        music_client = self.client.wavelink.get_player(ctx.guild.id)

        if music_client.channel:
            await music_client.pause(pause=pause)
            return True
        return None

    async def leave(self, ctx):
        """
        :param ctx: context
        :return: True or False
        """
        client = self.client.wavelink.get_player(ctx.guild.id)

        await client.disconnect()

    async def add_track_to_queue(self, ctx, tracks, arg):
        """
        :param ctx: context
        :param track: the track to add in the queue
        :return: True
        """

        music_client = self.client.wavelink.get_player(ctx.guild.id)

        if music_client.channel:
            music_client = self.client.wavelink.get_player(ctx.guild.id)

            tracks[0].channel = ctx.channel

            if len(tracks) <= 1:
                music_client.add(ctx.author, tracks[0])
            else:
                for track in tracks:
                    music_client.add(ctx.author, track)

            if not music_client.is_playing:
                if len(tracks) > 1:
                    length = len(tracks)
                    embed = Embed(description=f"Queued [**{length}** tracks]({arg}) !")
                    await ctx.send(embed=embed)
                return await self.play(ctx)
            if len(tracks) <= 1:
                embed = Embed(
                    description="Queued [{0.title}]({0.uri})".format(tracks[0])
                )
            else:
                length = len(tracks)
                embed = Embed(description=f"Queued [**{length}** tracks]({arg}) !")
            return await ctx.send(embed=embed)
        return

    async def search_track(self, ctx, query):
        """
        :param ctx: context
        :param arg: argument (url or keyword.s)
        :return: Track or None
        """
        client = self.client.wavelink.get_player(ctx.guild.id)

        if client.channel:
                track = await client.get_tracks(f"ytsearch:{query}").tracks
                return track
        return None

    def get_queue(self, ctx):
        """
        :param ctx: context
        :return: lavalink.Player.queue or None
        """

        music_client = self.client.wavelink.get_player(ctx.guild.id)

        if music_client is not None:
            return music_client.queue
        
        return
