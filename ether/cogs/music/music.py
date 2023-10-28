import datetime
import re
from typing import List

import requests
import mafic
import humanize
from discord.ext import commands
from discord import (
    ApplicationContext,
    Embed,
    Member,
    Option,
    SlashCommandGroup,
    OptionChoice,
)

from ether.core.i18n import _
from ether.core.constants import Colors
from ether.core.db.client import Database
from ether.core.utils import EtherEmbeds
from ether.core.config import config
from ether.core.constants import Emoji
from ether.core.voice_client import EtherPlayer
from ether.core.logging import log

PLAYLIST_REG = re.compile(
    r"^(?:http:\/\/|https:\/\/)?(?:www\.)?youtube\.com\/playlist\?list(?:\S+)?$"
)
PLAYLIST_ID = re.compile(r"[&?]list=([^&]+)")
URL_REG = re.compile(
    r"(?:https:\/\/|http:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*"
)


class Music(commands.Cog, name="music"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.MUSIC
        self.youtube_api_key = config.api.youtube.get("key")

        self.tape_in = open("ether/assets/sfx/tape_in.mp3", "rb").read()

    music = SlashCommandGroup("music", "Music commands!")

    async def cog_before_invoke(self, ctx):
        """Command before-invoke handler."""
        execeptions = ("playlist", "lavalinkinfo")
        if ctx.command.name in execeptions:
            return

        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def ensure_voice(self, ctx: ApplicationContext):
        """This check ensures that the bot and command author are in the same voicechannel."""
        player: EtherPlayer = ctx.guild.voice_client

        exceptions = ctx.command.name in ("playlist", "queue", "lavalinkinfo")
        should_connect = ctx.command.name in ("play", "join")

        if not exceptions and not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.respond(
                embed=EtherEmbeds.error("Join a voicechannel first."),
                ephemeral=True,
                delete_after=5,
            )

        if not player:
            if not should_connect:
                await ctx.respond(
                    embed=EtherEmbeds.error("Humm... There is no music."),
                    ephemeral=True,
                    delete_after=5,
                )

            permissions = (
                ctx.author.voice.channel.permissions_for(ctx.me)
                if ctx.author.voice
                else None
            )

            if permissions and (not permissions.connect or not permissions.speak):
                await ctx.respond(
                    embed=EtherEmbeds.error(
                        "I need the `CONNECT` and `SPEAK` permissions."
                    )
                )

            # Join
            if not isinstance(ctx.user, Member):
                return

            try:
                await ctx.user.voice.channel.connect(cls=EtherPlayer)
            except mafic.NoNodesAvailable:
                await ctx.respond(
                    embed=EtherEmbeds.error(
                        "Sorry, the bot isn't ready yet, please retry later!"
                    )
                )

                return False

            player: EtherPlayer = ctx.guild.voice_client

            setattr(player, "text_channel", ctx.channel)
        elif not ctx.author.voice or (player.channel.id != ctx.author.voice.channel.id):
            await ctx.respond(
                embed=EtherEmbeds.error("You need to be in my voicechannel."),
                ephemeral=True,
                delete_after=5,
            )

    @commands.slash_command(name="play")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _play(
        self,
        ctx: ApplicationContext,
        *,
        query: str,
        shuffle: bool = False,
        search_type=Option(
            name="search_type",
            choices=[
                OptionChoice("YouTube", value="ytsearch"),
                OptionChoice("YouTube Music", value="ytmsearch"),
                OptionChoice("SoundCloud", value="scsearch"),
            ],
            default="ytsearch",
        ),
    ):
        """Play a song from YouTube

        query:
            The song to search or play
        """
        await ctx.invoke(
            self.play, query=query, shuffle=shuffle, search_type=search_type
        )

    @music.command(name="play")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(
        self,
        ctx: ApplicationContext,
        *,
        query: str,
        shuffle: bool = False,
        search_type=Option(
            name="search_type",
            choices=[
                OptionChoice("YouTube", value="ytsearch"),
                OptionChoice("YouTube Music", value="ytmsearch"),
                OptionChoice("SoundCloud", value="scsearch"),
            ],
            default="ytsearch",
        ),
    ):
        """Play a song from YouTube (the same as /play)

        query:
            The song to search or play
        """

        player: EtherPlayer = ctx.guild.voice_client
        if not player:
            return

        await ctx.defer()

        if not player.node.available:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    f"Sorry, the node ({player.node.label}) is not available, please retry later!"
                )
            )
            return player.node.close()

        try:
            tracks = await player.fetch_tracks(query, search_type=search_type)
        except mafic.errors.TrackLoadException:
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    "Sorry, I can't play this track (can be copyight or blocked)"
                )
            )

        if not tracks:
            return await ctx.respond(embed=EtherEmbeds.error("Nothing found!"))

        if isinstance(tracks, mafic.Playlist):
            playlist_tracks = tracks.tracks
            player.queue.extend(playlist_tracks)

            if shuffle:
                player.queue.shuffle()

            await ctx.respond(
                embed=Embed(
                    description=f"**[{tracks.name}]({query})** - {len(playlist_tracks)} tracks",
                    color=Colors.DEFAULT,
                )
            )

            track = tracks.tracks[0]
        else:
            track = tracks[0]

            if not hasattr(player, "queue"):
                await player.disconnect()
                return await ctx.respond(
                    embed=EtherEmbeds.error("Please retry."), ephemeral=True
                )

            player.queue.append(track)
            await ctx.respond(
                embed=Embed(
                    description=f"Track added to queue: **[{track.title}]({track.uri})**",
                    color=Colors.DEFAULT,
                )
            )

        if not player.current:
            track = player.queue.get()
            await player.play(track)

    @music.command(name="stop")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stop(self, ctx: ApplicationContext):
        """Stop the current song"""
        player: EtherPlayer = ctx.guild.voice_client
        if not player:
            return

        if not player.connected:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    description="Player is not connected to a voice channel"
                ),
                delete_after=5,
            )
            return

        player.queue.clear()
        await player.stop()

        await ctx.respond(embed=Embed(description="🛑 Stopped"), delete_after=5)
        await player.disconnect()

    @music.command(name="pause")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pause(self, ctx: ApplicationContext):
        """Pause the current song"""
        player: EtherPlayer = ctx.guild.voice_client
        if not player:
            return

        if not player.current:
            await ctx.respond(
                embed=EtherEmbeds.error("I am not currently playing anything!"),
                delete_after=5,
            )
            return

        await player.pause(not player.paused)
        action = "▶️ Paused" if player.paused else "⏸️ Resume"
        await ctx.respond(embed=Embed(description=action), delete_after=5)

    @music.command(name="resume")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def resume(self, ctx: ApplicationContext):
        """Resume the current song"""
        player: EtherPlayer = ctx.guild.voice_client
        if not player:
            return

        if not player.paused:
            await ctx.respond(
                embed=EtherEmbeds.error("I am not paused!"), delete_after=5
            )
            return

        await player.resume()
        await ctx.respond(embed=Embed(description="⏸️ Resume"), delete_after=5)

    @music.command(name="skip")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skip(self, ctx: ApplicationContext):
        """Skip the current song"""
        player: EtherPlayer = ctx.guild.voice_client
        if not player:
            return

        if not len(player.queue):
            return await ctx.respond(
                embed=EtherEmbeds.error(description="There's nothing to skip"),
                delete_after=5,
            )

        await player.play(player.queue.get())
        return await ctx.respond(embed=Embed(description="⏭️ Skip"), delete_after=5)

    @music.command(name="shuffle")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shuffle(self, ctx: ApplicationContext):
        """Shuffle the queue"""
        player: EtherPlayer = ctx.guild.voice_client
        if not player:
            return

        player.queue.shuffle()

        await ctx.respond(
            embed=Embed(
                description="The queue has been shuffled!", color=Colors.DEFAULT
            ),
            delete_after=10,
        )
        return player.queue

    @music.command(name="queue")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx: ApplicationContext):
        """Show the current queue"""
        player: EtherPlayer = ctx.guild.voice_client

        if not player.current:
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    "There are no tracks in the queue or currently playing!"
                ),
                ephemeral=True,
            )

        embed = Embed(title=":notes: Queue:")
        if player.current:
            first_track = player.current
            embed.add_field(
                name="Now Playing:",
                value=f'`1.` [{first_track.title}]({first_track.uri}) | `{"🔴 Stream" if first_track.stream else datetime.timedelta(milliseconds=first_track.length)}`',
                inline=False,
            )

        queue = player.queue.copy()

        next_track_label = []
        for _ in range(10):
            if queue.is_empty:
                break
            track = queue.get()
            title = track.title
            if len(track.title) > 35:
                title = f"{title[:32]} ..."
            next_track_label.append(
                f"`{player.queue.index(track) + 2}.` [{title}]({track.uri}) | "
                f"`{'🔴 Stream' if track.stream else datetime.timedelta(milliseconds=track.length)}`"
            )

        if next_track_label:
            embed.add_field(
                name="Next 10 Tracks:", value="\n".join(next_track_label), inline=False
            )

        return await ctx.respond(embed=embed)

    @music.command(name="loop")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def loop(self, ctx: ApplicationContext):
        """Loop the current song"""

        player: EtherPlayer = ctx.guild.voice_client

        if not player:
            return

        if not player.loop:
            player.loop = True
            await ctx.respond(embed=Embed(description="🔁 Loop enabled"), delete_after=5)
        else:
            player.loop = False
            await ctx.respond(
                embed=Embed(description="🔁 Loop disabled"), delete_after=5
            )

    @music.command(name="playlist")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def playlist(self, ctx: ApplicationContext, playlist_link: str):
        """Setup a playlist player for a YouTube playlist"""

        if not ctx.channel.permissions_for(self.user).send_messages:
            return await ctx.respond(
                embed=EtherEmbeds.error("Please allow me to send messages!"),
                ephemeral=True,
                delete_after=5,
            )

        # Check if the guild can have a new playlist
        if not await Database.Playlist.guild_limit(ctx.guild.id):
            return await ctx.respond(
                embed=EtherEmbeds.error("You can't have more than 10 playlists!")
            )

        if not re.match(PLAYLIST_REG, playlist_link):
            return await ctx.respond(
                embed=EtherEmbeds.error("The url is incorrect!"),
                ephemeral=True,
                delete_after=5,
            )

        playlist_id = re.search(PLAYLIST_ID, playlist_link).groups()[0]

        key = config.api.youtube.get("key")

        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/playlists?part=snippet&part=contentDetails&id={playlist_id}&key={key}"
        )
        if not r.ok:
            ctx.respond(
                embed=EtherEmbeds.error("Could not find the playlist!"), delete_after=5
            )

        r = r.json()
        if not r["items"]:
            return await ctx.respond(
                embed=EtherEmbeds.error(
                    "Could not find the playlist! Please make sure to put the playlist in public or not listed"
                ),
                delete_after=5,
            )
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

        await Database.Playlist.create(message.id, message.guild.id, playlist_id)

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
    async def lavalink_info(self, ctx: ApplicationContext):
        """Show lavalink info"""
        return  # FIXME: lavalink_info is not working
        lavalink = None
        embed = Embed(title=f"**Mafic:** `{mafic.__version__}`", color=Colors.DEFAULT)

        embed.add_field(
            name="Server",
            value=f"Server Nodes: `{len(self.client.NodePool.nodes)}`\n"
            f"Voice Client Connected: `{len(self.client.voice_clients)}`\n",
            inline=False,
        )

        for node in self.client.NodePool.nodes:
            embed.add_field(
                name=f"Node: {node.name}",
                value=f"Node Memory: `{humanize.naturalsize(node.stats.memory_used)}/{humanize.naturalsize(node.stats.memory_allocated)}` | `({humanize.naturalsize(node.stats.memory_free)} free)`\n"
                f"Node CPU: `{node.stats.cpu_cores}`\n"
                f"Node Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`\n"
                f"Node Players: `{len(node.players)}`\n",
                inline=False,
            )
        await ctx.respond(embed=embed)
