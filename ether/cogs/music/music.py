import datetime
import os
import re
from typing import Optional
import random

import discord
import requests
import wavelink
import humanize
from discord.ext import commands
from discord import ApplicationContext, Embed, SlashCommandGroup
from ether.core.i18n import _

from ether.core.constants import Colors
from ether.core.db.client import Database, Guild, Playlist
from ether.core.logging import log
from ether.core.utils import EtherEmbeds
from ether.core.config import config
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji

PLAYLIST_REG = re.compile(
    r"^(?:http:\/\/|https:\/\/)?(?:www\.)?youtube\.com\/playlist\?list(?:\S+)?$"
)
PLAYLIST_ID = re.compile(r"[&?]list=([^&]+)")
URL_REG = re.compile(
    r"(?:https:\/\/|http:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*"
)


class Player(wavelink.Player):
    def __init__(self, text_channel: Optional[discord.TextChannel]):
        super().__init__()
        self.message: Optional[discord.Message] = None
        self.text_channel = text_channel
        self.queue: wavelink.Queue = wavelink.Queue(max_size=100)


class Music(commands.Cog, name="music"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.MUSIC

        self.youtube_api_key = config.api.youtube.get("key")

        client.loop.create_task(self.connect_nodes())

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        message_id = payload.message_id

        playlist = await Playlist.from_id(message_id)
        if not playlist:
            return

        channel = payload.member.guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(message_id)
        reaction = [r for r in message.reactions if r.emoji.name == payload.emoji.name][
            0
        ]

        await reaction.remove(payload.member)

        emoji = payload.emoji
        if emoji.id in (990260523692064798, 990260524686139432):  # Play
            if not payload.member.voice:
                return
            if not payload.member.guild.voice_client:
                db_guild = await Guild.from_id(payload.member.guild.id)

                text_channel = (
                    payload.member.guild.get_channel(db_guild.music_channel_id) or None
                )
                player = Player(text_channel=text_channel)
                vc: Player = await payload.member.voice.channel.connect(cls=player)
                vc.queue = wavelink.Queue(max_size=100)
                vc.text_channel = text_channel
                await payload.member.guild.change_voice_state(
                    channel=payload.member.voice.channel,
                    self_mute=False,
                    self_deaf=True,
                )
            else:
                vc: Player = payload.member.guild.voice_client

            if len(vc.queue) > 0:
                return

            tracks = await vc.node.get_playlist(
                cls=wavelink.YouTubePlaylist, identifier=playlist.playlist_link
            )
            if tracks:
                shuffle = emoji.id == 990260524686139432
                if shuffle:
                    random.shuffle(tracks.tracks)
                for t in tracks.tracks:
                    vc.queue.put(t)

            if not vc.is_playing():
                track = vc.queue.get()
                await vc.play(track)
        elif emoji.id == 990260521355862036:  # back
            pass
        elif emoji.id == 990260522521858078:  # skip
            vc: Player = await self.connect_with_payload(payload)

            if not vc:
                return

            if vc.queue.is_empty:
                return

            await vc.play(vc.queue.get(), replace=True)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        r_message = await Playlist.from_id(payload.message_id)
        if r_message:
            await r_message.delete()

    async def connect_nodes(self):
        await self.client.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.client,
            host=config.lavalink.get("host"),
            port=config.lavalink.get("port"),
            password=config.lavalink.get("pass"),
            https=config.lavalink.get("https"),
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
        if channel := player.text_channel:
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

        if reason not in ("FINISHED", "STOPPED", "REPLACED"):
            if player.text_channel:
                return await player.text_channel.send(
                    embed=EtherEmbeds.error(f"Track finished for reason `{reason}`")
                )

            log.warn(f"Track finished for reason `{reason}`")

        if not player.queue.is_empty and reason != "REPLACED":
            await player.play(player.queue.get())

        if player.message:
            await player.message.delete()

    async def connect_with_payload(self, payload) -> Optional[Player]:
        if not payload.member.voice:
            return None
        if not payload.member.guild.voice_client:
            db_guild = await Guild.from_id(payload.member.guild.id)

            text_channel = (
                payload.member.guild.get_channel(db_guild.music_channel_id) or None
            )
            player = Player(text_channel=text_channel)
            vc: Player = await payload.member.voice.channel.connect(cls=player)
            vc.queue = wavelink.Queue(max_size=100)
            vc.text_channel = text_channel
            await payload.member.guild.change_voice_state(
                channel=payload.member.voice.channel, self_mute=False, self_deaf=True
            )
        else:
            vc: Player = payload.member.guild.voice_client

        return vc

    @music.command(name="join")
    @commands.guild_only()
    @locale_doc
    async def _connect(self, ctx: ApplicationContext) -> Optional[Player]:
        """Connect the bot to your voice channel"""

        if not ctx.author.voice:
            await ctx.respond(embed=EtherEmbeds.error("Please join a channel."))
            return None
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            player = Player(text_channel=ctx.channel)
            vc: Player = await ctx.user.voice.channel.connect(cls=player)
            vc.queue = wavelink.Queue(max_size=100)
            vc.text_channel = ctx.channel
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=False, self_deaf=True
            )

            if ctx.command.qualified_name == "music join":
                await ctx.respond(
                    embed=Embed(description=f"`{ctx.author.voice.channel}` joined")
                )
        else:
            vc: Player = ctx.guild.voice_client

        return vc

    @music.command(name="leave")
    @commands.guild_only()
    @locale_doc
    async def _disconnect(self, ctx: ApplicationContext):
        """Disconnect the bot from your voice channel"""

        vc: Player = await self._connect(ctx)

        # Check if the voice client channel is the same as the user's voice channel.
        if vc.channel.id == vc.channel.id:
            await vc.disconnect()

            await ctx.respond(
                embed=Embed(description=f"`{ctx.author.voice.channel}` leave")
            )
            return vc

    @music.command(name="search")
    @commands.guild_only()
    @locale_doc
    async def search(self, ctx: ApplicationContext, *, search: wavelink.YouTubeTrack):
        """Search a song on YouTube"""
        print(search)

    @music.command(name="play")
    @commands.guild_only()
    @locale_doc
    async def _play(self, ctx: ApplicationContext, *, query: str):
        """Play a song from YouTube"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        if ctx.user.voice.channel.id != vc.channel.id and vc.is_playing:
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    "I'm already playing music in an other channel."
                ),
                delete_after=5,
            )

        # Search for playlist
        if re.match(PLAYLIST_REG, query):
            try:
                playlist = await vc.node.get_playlist(
                    cls=wavelink.YouTubePlaylist, identifier=query
                )
                if playlist:
                    for t in playlist.tracks:
                        vc.queue.put(t)

                    await ctx.respond(
                        embed=Embed(
                            description=f"**[{len(playlist.tracks)} tracks]** added to queue!",
                            color=Colors.DEFAULT,
                        )
                    )
            except wavelink.errors.LavalinkException:
                return await ctx.respond(
                    embed=EtherEmbeds.error(
                        "I did not find any playlists with this url."
                    ),
                    delete_after=5,
                )
        else:
            tracks = await vc.node.get_tracks(
                cls=wavelink.YouTubeTrack, query=f"ytsearch:{query}"
            )

            if not tracks:
                if re.match(URL_REG, query):
                    return await ctx.respond(
                        embed=EtherEmbeds.error(
                            "I did not find any songs with this url."
                        ),
                        delete_after=5,
                    )
                else:
                    return await ctx.respond(
                        embed=EtherEmbeds.error(
                            "I did not find any songs with this query."
                        ),
                        delete_after=5,
                    )
            track = tracks[0]

            vc.queue.put(track)

            await ctx.respond(
                embed=Embed(
                    description=f"Track added to queue: **[{track.title}]({track.uri})**",
                    color=Colors.DEFAULT,
                )
            )

        if not vc.is_playing():
            track = vc.queue.get()
            await vc.play(track)

    @music.command(name="stop")
    @commands.guild_only()
    @locale_doc
    async def _stop(self, ctx: ApplicationContext):
        """Stop the current song"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        vc.queue.clear()
        await vc.stop()

        await ctx.respond(embed=Embed(description="🛑 Stopped"), delete_after=5)

    @music.command(name="pause")
    @commands.guild_only()
    @locale_doc
    async def pause(self, ctx: ApplicationContext):
        """Pause the current song"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        if not vc.is_playing:
            await ctx.respond(
                embed=EtherEmbeds.error("I am not currently playing anything!"),
                delete_after=5,
            )
            return

        await vc.set_pause(not vc.is_paused())
        action = "▶️ Paused" if vc.is_paused() else "⏸️ Resume"
        await ctx.respond(embed=Embed(description=action), delete_after=5)

    @music.command(name="resume")
    @commands.guild_only()
    @locale_doc
    async def resume(self, ctx: ApplicationContext):
        """Resume the current song"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        if not vc.is_paused():
            await ctx.respond(
                embed=EtherEmbeds.error("I am not paused!"), delete_after=5
            )
            return

        await vc.set_pause(False)
        await ctx.respond(embed=Embed(description="⏸️ Resume"), delete_after=5)

    @music.command(name="skip")
    @commands.guild_only()
    @locale_doc
    async def _skip(self, ctx: ApplicationContext):
        """Skip the current song"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        if vc.queue.is_empty:
            return

        await vc.play(vc.queue.get(), replace=True)
        return await ctx.respond(embed=Embed(description="⏭️ Skip"), delete_after=5)

    @music.command(name="shuffle")
    @commands.guild_only()
    @locale_doc
    async def _shuffle(self, ctx: ApplicationContext):
        """Shuffle the queue"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        shuffled_queue = vc.queue.copy()
        shuffled_queue = list(shuffled_queue)
        random.shuffle(shuffled_queue)
        vc.queue.clear()

        for tracks in shuffled_queue:
            vc.queue.put(tracks)

        await ctx.respond(
            embed=Embed(
                description="The queue has been shuffled!", color=Colors.DEFAULT
            ),
            delete_after=10,
        )
        return vc.queue

    @music.command(name="queue")
    @commands.guild_only()
    @locale_doc
    async def queue(self, ctx: ApplicationContext):
        """Show the current queue"""
        vc: Player = await self._connect(ctx)

        if not vc:
            return

        if not vc.source:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error has occurred!"), ephemeral=True
            )

        queue = vc.queue.copy()

        first_track = vc.source
        embed = Embed(title=":notes: Queue:")
        embed.add_field(
            name="Now Playing:",
            value=f'`1.` [{first_track.title}]({first_track.uri[:30]}) | `{"🔴 Stream" if first_track.is_stream() else datetime.timedelta(seconds=first_track.length)}`',
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

        await ctx.respond(embed=embed)

        return

    @music.command(name="playlist")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @locale_doc
    async def playlist(self, ctx: ApplicationContext, playlist_link):
        """Play a playlist from youtube"""
        if not re.match(PLAYLIST_REG, playlist_link):
            ctx.respond(
                embed=EtherEmbeds.error("The url is incorrect!"), delete_after=5
            )

        id = re.search(PLAYLIST_ID, playlist_link).groups()[0]

        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/playlists?part=snippet&part=contentDetails&id={id}&key={self.youtube_api_key}"
        )
        if not r.ok:
            ctx.respond(
                embed=EtherEmbeds.error("Could not find the playlist!"), delete_after=5
            )

        r = r.json()
        data = r["items"][0]["snippet"]
        embed = Embed(title=f"[Playlist] {data['title']}", url=playlist_link)
        embed.set_thumbnail(url=data["thumbnails"]["default"]["url"])
        embed.description = (
            f"*(The queue must be empty to be played)*\n\n{data['description']}"
        )
        embed.add_field(
            name="Tracks",
            value=f"{r['items'][0]['contentDetails']['itemCount']} tracks",
        )
        embed.set_footer(text=f"Created by {data['channelTitle']}")

        message = await ctx.send(embed=embed)
        await Database.Playlist.create(message.id, playlist_link)

        await message.add_reaction("<:back:990260521355862036>")
        await message.add_reaction("<:play:990260523692064798>")
        await message.add_reaction("<:next:990260522521858078>")
        await message.add_reaction("<:shuffle:990260524686139432>")

        await ctx.respond(
            "Playlist successfuly created!", ephemeral=True, delete_after=5
        )

    @music.command(name="lavalinkinfo")
    @commands.guild_only()
    @commands.is_owner()
    @locale_doc
    async def lavalink_info(self, ctx: ApplicationContext):
        """Show lavalink info"""
        player = ctx.guild.voice_client
        if not player:
            return
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

        await ctx.channel.send(embed=embed)
