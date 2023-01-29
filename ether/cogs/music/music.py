import datetime
import re
from typing import Optional
import random

import requests
import lavalink
import humanize
from discord.ext import commands
from discord import ApplicationContext, Embed, SlashCommandGroup
from ether.core.i18n import _

from ether.core.constants import Colors
from ether.core.db.client import Database
from ether.core.utils import EtherEmbeds
from ether.core.config import config
from ether.core.constants import Emoji
from ether.core.music import Player
from ether.core.voice_client import LavalinkVoiceClient

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

        client.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.client.wait_until_ready()

        if not hasattr(
            self.client, "lavalink"
        ):  # This ensures the client isn't overwritten during cog reloads.
            self.client.lavalink = lavalink.Client(self.client.user.id)
            self.client.lavalink.add_node(
                config.lavalink.get("host"),
                config.lavalink.get("port"),
                config.lavalink.get("pass"),
                "eu",
                "default-node",
                ssl=config.lavalink.get("https"),
            )

        lavalink.add_event_hook(self.track_hook)

    music = SlashCommandGroup("music", "Music commands!")

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.client.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """Command before-invoke handler."""
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """This check ensures that the bot and command author are in the same voicechannel."""
        player = self.client.lavalink.player_manager.create(ctx.guild.id)

        should_connect = ctx.command.name in ("play", "join")

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError("Join a voicechannel first.")

        v_client = ctx.voice_client
        if not v_client:
            if not should_connect:
                raise commands.CommandInvokeError("Not connected.")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError(
                    "I need the `CONNECT` and `SPEAK` permissions."
                )

            player.store("channel", ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError("You need to be in my voicechannel.")

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = event.player.guild_id
            guild = self.client.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

    @music.command(name="join")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def join(self, ctx: ApplicationContext) -> Optional[Player]:
        """Connect the bot to your voice channel"""

        self.client.lavalink.player_manager.get(ctx.guild.id)

        await ctx.respond(
            embed=Embed(description=f"`{ctx.author.voice.channel}` joined")
        )

    @music.command(name="leave")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leave(self, ctx: ApplicationContext):
        """Disconnect the bot from your voice channel"""

        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send(embed=EtherEmbeds.error("Not connected."))

        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):

            return await ctx.send("You're not in my voicechannel!")

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.respond(
            embed=Embed(description=f"`{ctx.author.voice.channel}` leave")
        )

    @music.command(name="play")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx: ApplicationContext, *, query: str):
        """Play a song from YouTube"""
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not URL_REG.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results.tracks:
            return await ctx.respond(embed=EtherEmbeds.error("Nothing found!"))

        if results.load_type == "PLAYLIST_LOADED":
            tracks = results.tracks

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

                await ctx.respond(
                    embed=Embed(
                        description=f"{results.playlist_info.name} - {len(tracks)} tracks",
                        color=Colors.DEFAULT,
                    )
                )
        else:
            track = results.tracks[0]
            player.add(requester=ctx.author.id, track=track)

            await ctx.respond(
                embed=Embed(
                    description=f"Track added to queue: **[{track.title}]({track.uri})**",
                    color=Colors.DEFAULT,
                )
            )

        if not player.is_playing:
            await player.play()

    @music.command(name="stop")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stop(self, ctx: ApplicationContext):
        """Stop the current song"""
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        player.queue.clear()
        await player.stop()

        await ctx.respond(embed=Embed(description="🛑 Stopped"), delete_after=5)

    @music.command(name="pause")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pause(self, ctx: ApplicationContext):
        """Pause the current song"""
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            await ctx.respond(
                embed=EtherEmbeds.error("I am not currently playing anything!"),
                delete_after=5,
            )
            return

        await player.set_pause(not player.paused)
        action = "▶️ Paused" if player.paused else "⏸️ Resume"
        await ctx.respond(embed=Embed(description=action), delete_after=5)

    @music.command(name="resume")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def resume(self, ctx: ApplicationContext):
        """Resume the current song"""
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.paused:
            await ctx.respond(
                embed=EtherEmbeds.error("I am not paused!"), delete_after=5
            )
            return

        await player.set_pause(False)
        await ctx.respond(embed=Embed(description="⏸️ Resume"), delete_after=5)

    @music.command(name="skip")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skip(self, ctx: ApplicationContext):
        """Skip the current song"""
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not len(player.queue):
            return

        await player.skip()
        return await ctx.respond(embed=Embed(description="⏭️ Skip"), delete_after=5)

    @music.command(name="shuffle")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _shuffle(self, ctx: ApplicationContext):
        """Shuffle the queue"""
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        player.set_shuffle(True)

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
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error has occurred!"), ephemeral=True
            )

        queue = player.queue.copy()

        first_track = player.current
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
                f"`{player.queue.index(track) + 2}.` [{title}]({track.uri}) | "
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def playlist(self, ctx: ApplicationContext, playlist_link: str):
        """Setup a playlist player for a YouTube playlist"""

        # Check if the guild can have a new playlist
        if not Database.Playlist.guild_limit(ctx.guild.id):
            return await ctx.respond(
                emned=EtherEmbeds.error("You can't have more than 10 playlists!")
            )

        if not re.match(PLAYLIST_REG, playlist_link):
            return await ctx.respond(
                embed=EtherEmbeds.error("The url is incorrect!"),
                ephemeral=True,
                delete_after=5,
            )

        playlist_id = re.search(PLAYLIST_ID, playlist_link).groups()[0]

        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/playlists?part=snippet&part=contentDetails&id={playlist_id}&key={self.youtube_api_key}"
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
        await Database.Playlist.create(message.id, playlist_id)

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
        embed = Embed(
            title=f"**WaveLink:** `{lavalink.__version__}`", color=Colors.DEFAULT
        )

        embed.add_field(
            name="Server",
            value=f"Server Nodes: `{len(lavalink.NodeManager.nodes)}`\n"
            f"Voice Client Connected: `{len(self.client.voice_clients)}`\n",
            inline=False,
        )

        for node in lavalink.NodePool.nodes:
            embed.add_field(
                name=f"Node: {node.name}",
                value=f"Node Memory: `{humanize.naturalsize(node.stats.memory_used)}/{humanize.naturalsize(node.stats.memory_allocated)}` | `({humanize.naturalsize(node.stats.memory_free)} free)`\n"
                f"Node CPU: `{node.stats.cpu_cores}`\n"
                f"Node Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`\n"
                f"Node Players: `{len(node.players)}`\n",
                inline=False,
            )
        await ctx.respond(embed=embed)
