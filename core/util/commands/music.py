import urllib.parse
import lavalink

from youtubesearchpython import VideosSearch
from core.util.lavalinkmanager import LavalinkManager

from discord import Embed

import os


class MusicCommandsManager:
    def __init__(self, client):
        self.client = client
        self.lavalink = None

    async def init(self):
        self.lavalink = LavalinkManager(
            self.client,
            host=os.getenv("LAVALINK_HOST"),
            password=os.getenv("LAVALINK_PASS"),
            rest_port=os.getenv("LAVALINK_PORT"),
            ws_port=os.getenv("LAVALINK_PORT"),
        )

        await self.lavalink.initialize_lavalink()

    def get_client(self, guild_id):
        """
        :param guild_id: the guild id
        :return: lavalink.Player or None
        """

        return lavalink.get_player(guild_id=guild_id)

    async def user_is_in_client_channel(self, ctx):
        """
        Return if a user is in the same voice channel as the bot.
        :param ctx: context
        :param music_client: lavalink.Player
        :return: True or False
        """

        music_client = self.get_client(ctx.guild.id)

        if music_client is None:
            await self.join_voice_channel(ctx)
            return True

        if music_client and music_client.channel:
            if ctx.author.voice and ctx.author.voice.channel == music_client.channel:
                return True

        return False

    async def join_voice_channel(self, ctx):
        """
        :param ctx: context
        :return: String or lavalink.Player
        """

        music_client = self.get_client(ctx.guild.id)

        if music_client and music_client.channel:
            return "I'm already connected in a voice channel."

        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
            await lavalink.connect(voice_channel)
        else:
            return "You must be connected to a voice channel."

        return

    async def play(self, ctx):
        """
        :param ctx: context
        :return: True or None
        """

        music_client = self.get_client(ctx.guild.id)

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

        music_client = self.get_client(ctx.guild.id)

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
        music_client = self.get_client(ctx.guild.id)

        if music_client.channel:
            await music_client.pause(pause=pause)
            return True
        return None

    async def leave(self, ctx):
        """
        :param ctx: context
        :return: True or False
        """
        music_client = self.get_client(ctx.guild.id)

        if music_client.channel:
            await music_client.disconnect()

    async def add_track_to_queue(self, ctx, tracks, arg):
        """
        :param ctx: context
        :param track: the track to add in the queue
        :return: True
        """

        music_client = self.get_client(ctx.guild.id)

        if music_client.channel:
            music_client = self.get_client(ctx.guild.id)

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

    async def search_track(self, ctx, arg, args):
        """
        :param ctx: context
        :param arg: argument (url or keyword.s)
        :return: Track or None
        """
        music_client = self.get_client(ctx.guild.id)

        domain = urllib.parse.urlsplit(arg).netloc
        if music_client.channel:
            if domain != "" and ("youtube.com" in domain or "soundcloud.com" in domain):
                load_result = await music_client.load_tracks(arg)
                result = load_result.tracks
                return result
            if domain == "":
                videos_search = VideosSearch(" ".join(args), limit=1)
                url = videos_search.result()["result"][0]["link"]
                result = []
                track = await music_client.load_tracks(url)
                if track and track.tracks and track.tracks[0]:
                    result.append(track.tracks[0])
                    return result
        return None

    def get_queue(self, ctx):
        """
        :param ctx: context
        :return: lavalink.Player.queue or None
        """

        music_client = self.get_client(ctx.guild.id)

        if music_client is not None:
            return music_client.queue
        
        return
