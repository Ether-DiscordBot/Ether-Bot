import datetime
import random
import re
from typing import Optional, cast

import discord
import requests
import wavelink
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from ether.core.config import config
from ether.core.constants import Colors, Emoji
from ether.core.db.client import Database
from ether.core.embed import Embed
from ether.core.i18n import _
from ether.core.logging import log

PLAYLIST_REG = re.compile(
    r"^(?:http:\/\/|https:\/\/)?(?:www\.)?youtube\.com\/playlist\?list(?:\S+)?$"
)
PLAYLIST_ID = re.compile(r"[&?]list=([^&]+)")
URL_REG = re.compile(
    r"(?:https:\/\/|http:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*"
)


# FIXME: I think it's because GroupCog is in conflict with Group
class Music(commands.GroupCog, group_name="music"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.MUSIC
        self.youtube_api_key = config.api.youtube.get("key")

        self.tape_in = open("ether/assets/sfx/tape_in.mp3", "rb").read()

    filter = app_commands.Group(
        name="filter", description="Music filters related commands"
    )

    async def interaction_check(self, interaction: discord.Interaction):
        """Command before-invoke handler."""

        exceptions = ("playlist", "lavalinkinfo")
        if interaction.command.name in exceptions:
            return

        guild_check = interaction.guild != None

        if guild_check:
            return await self.ensure_voice(interaction)

        return guild_check

    async def ensure_voice(self, interaction: discord.Interaction) -> bool:
        """This check ensures that the bot and command author are in the same voicechannel."""

        exceptions = interaction.command.name in ("playlist", "queue", "lavalinkinfo")
        should_connect = interaction.command.name in ("play", "join")

        if (
            not exceptions
            and not interaction.user.voice
            or not interaction.user.voice.channel
        ):
            await interaction.response.send_message(
                embed=Embed.error(description="Join a voicechannel first."),
                ephemeral=True,
                delete_after=5,
            )
            return False

        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore

        if not player or not player.connected:
            if not should_connect:
                await interaction.response.send_message(
                    embed=Embed.error(description="There is no music."),
                    ephemeral=True,
                    delete_after=5,
                )
                return False

            permissions = (
                interaction.user.voice.channel.permissions_for(
                    interaction.guild.me
                )
                if interaction.user.voice
                else None
            )

            if permissions and (not permissions.connect or not permissions.speak):
                await interaction.response.send_message(
                    embed=Embed.error(description="I need the `CONNECT` and `SPEAK` permissions.")
                )
                return False

            # Join
            try:
                await interaction.user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            except wavelink.WavelinkException:
                await interaction.response.send_message(
                    embed=Embed.error(
                        description="Sorry, an error occurred. Please retry later or report the issue."
                    )
                )

                return False
        elif not interaction.user.voice or (
            player.channel.id != interaction.user.voice.channel.id
        ):
            await interaction.response.send_message(
                embed=Embed.error(description="You need to be in my voicechannel."),
                ephemeral=True,
                delete_after=5,
            )
            return False

        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore

        # Lock the player to this channel...
        if player and not hasattr(player, "home"):
            player.home = interaction.channel
        elif player and player.home != interaction.channel:
            await interaction.response.send_message(Embed.error(description=f"You can only play songs in {player.home.mention}, as the player has already started there."), ephemeral=True, delete_after=5)

        return True

    @app_commands.command(name="play")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(
        source=[
            Choice(name="YouTube", value=0),
            Choice(name="YouTube Music", value=1),
            Choice(name="SoundCloud", value=2),
        ]
    )
    async def play(
        self,
        interaction: discord.Interaction,
        *,
        query: str,
        shuffle: bool = False,
        source: Choice[int] = 0,
        auto_play: bool = False,
    ):
        """Play a song from YouTube

        query:
            The song to search or play
        """

        return await self._play(interaction, query=query, shuffle=shuffle, source=source, auto_play=auto_play)


    @app_commands.command(name="play")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(
        source=[
            Choice(name="YouTube", value=0),
            Choice(name="YouTube Music", value=1),
            Choice(name="SoundCloud", value=2),
        ]
    )
    async def music_play(
        self,
        interaction: discord.Interaction,
        *,
        query: str,
        shuffle: bool = False,
        source: Choice[int] = 0,
        auto_play: bool = True,
    ):
        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore

        if not player:
            return

        if auto_play:
            player.autoplay = wavelink.AutoPlayMode.enabled

        if hasattr(source, "value"):
            source = source.value

        tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource(source))
        if not tracks:
            return await interaction.response.send_message(
                embed=Embed.error(description="No tracks were found!")
            )

        if isinstance(tracks, wavelink.Playlist):
            playlist_tracks = tracks.tracks
            if shuffle:
                random.shuffle(playlist_tracks)

            added: int = await player.queue.put_wait(playlist_tracks)

            await interaction.response.send_message(
                embed=Embed(
                    description=f"**[{tracks.name}]({query})** - {len(added)} tracks",
                    color=Colors.DEFAULT,
                )
            )
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.response.send_message(
                embed=Embed(
                    description=f"Track added to queue: **[{track.title}]({track.uri})**",
                    color=Colors.DEFAULT,
                )
            )

        if not player.playing:
            await player.play(player.queue.get())


    @app_commands.command(name="stop")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def stop(self, interaction: discord.Interaction):
        """Stop the current song"""
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message(
                embed=Embed.error(
                    description="Player is not connected to a voice channel"
                ),
                delete_after=5,
            )

        if not player.connected:
            await interaction.response.send_message(
                embed=Embed.error(
                    description="Player is not connected to a voice channel"
                ),
                delete_after=5,
            )
            return

        player.queue.clear()
        await player.stop()

        await interaction.response.send_message(
            embed=Embed(description="🛑 Stopped"), delete_after=5
        )
        await player.disconnect()

    @app_commands.command(name="pause")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def pause(self, interaction: discord.Interaction):
        """Pause the current song"""
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return

        if not player.current:
            await interaction.response.send_message(
                embed=Embed.error(description="I am not currently playing anything!"),
                delete_after=5,
            )
            return

        await player.pause(not player.paused)
        action = "▶️ Paused" if player.paused else "⏸️ Resume"
        await interaction.response.send_message(
            embed=Embed(description=action), delete_after=5
        )

    @app_commands.command(name="resume")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def resume(self, interaction: discord.Interaction):
        """Resume the current song"""
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return

        if not player.paused:
            await interaction.response.send_message(
                embed=Embed.error(description="I am not paused!"), delete_after=5
            )
            return

        await player.resume()
        await interaction.response.send_message(
            embed=Embed(description="⏸️ Resume"), delete_after=5
        )

    @app_commands.command(name="skip")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def skip(self, interaction: discord.Interaction):
        """Skip the current song"""
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return

        skipped = await player.skip(force=True)

        if not skipped:
            return await interaction.response.send_message(
                embed=Embed.error(description="There's nothing to skip"),
                delete_after=5,
            )

        return await interaction.response.send_message(
            embed=Embed(description="⏭️ Skip"), delete_after=5
        )

    @app_commands.command(name="shuffle")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def shuffle(self, interaction: discord.Interaction):
        """Shuffle the queue"""
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return

        player.queue.shuffle()

        await interaction.response.send_message(
            embed=Embed(
                description="The queue has been shuffled!", color=Colors.DEFAULT
            ),
            delete_after=10,
        )
        return player.queue

    @app_commands.command(name="queue")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: discord.Interaction):
        """Show the current queue"""
        player: wavelink.Player = interaction.guild.voice_client

        embed = Embed(title=":notes: Queue:")

        if player.current:
            if player.current:
                first_track: wavelink.Playable = player.current
                embed.add_field(
                    name="Now Playing:",
                    value=f'`1.` [{first_track.title}]({first_track.uri}) | `{"🔴 Stream" if first_track.is_stream else datetime.timedelta(milliseconds=first_track.length)}`',
                    inline=False,
                )


        next_track_label = []

        # Classic queue tracks
        for idx, track in enumerate(player.queue[:9]):
            title = track.title
            if len(track.title) > 35:
                title = f"{title[:32]} ..."
            next_track_label.append(
                f"`{idx + 2}.` [{title}]({track.uri}) | "
                f"`{'🔴 Stream' if track.is_stream else datetime.timedelta(milliseconds=track.length)}`"
            )


        # Auto queue tracks
        if len(player.auto_queue) > 0 and len(next_track_label) < 9:
            next_track_label.append(
                "↓ The following tracks come from the `autoplay` mode. ↓"
            )
            for idx, track in enumerate(player.auto_queue[:9]):
                title = track.title
                if len(track.title) > 35:
                    title = f"{title[:32]} ..."
                next_track_label.append(
                    f"*`{idx + 1}.` [{title}]({track.uri}) | "
                    f"`{'🔴 Stream' if track.is_stream else datetime.timedelta(milliseconds=track.length)}`*"
                )


        if next_track_label:
            embed.add_field(
                name=f"Next {len(next_track_label)} Tracks:", value="\n".join(next_track_label[:9]), inline=False
            )


        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="autoplay")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def autoplay(self, interaction: discord.Interaction, *, enabled: bool = None):
        "Toggle the auto play"
        player: wavelink.Player = interaction.guild.voice_client

        if enabled is None:
            enabled = not player.autoplay == wavelink.AutoPlayMode.enabled

        if enabled:
            player.autoplay = wavelink.AutoPlayMode.enabled
            return await interaction.response.send_message(Embed(description="✅ Auto play enabled"))

        player.autoplay = wavelink.AutoPlayMode.disabled
        return await interaction.response.send_message(Embed(description="✅ Auto play disabled"))

    @app_commands.command(name="back")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def back(self, interaction: discord.Interaction):
        "Play the previous track (works approximately)"
        player: wavelink.Player = interaction.guild.voice_client

        try:
            if not player.current:
                raise wavelink.QueueEmpty()

            track: wavelink.Playable
            if player.current.recommended and len(player.auto_queue.history) > 1:
                t_idx = len(player.auto_queue.history) - 2

                track = player.auto_queue.history[t_idx]
                await player.auto_queue.history.delete(t_idx)
            else:
                t_idx = len(player.queue.history) - 2

                track = player.queue.history[t_idx]
                await player.queue.history.delete(t_idx)
        except (wavelink.QueueEmpty, ValueError):
            return await interaction.response.send_message(Embed.error(description="There is no previous track"), ephemeral=True, delete_after=5.0)

        await player.play(track, replace=True)

        return await interaction.response.send_message(Embed(description="⏮️ Playing previous track"), delete_after=5.0)

    @app_commands.command(name="history")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def history(self, interaction: discord.Interaction):
        """Show the current queue"""
        player: wavelink.Player = interaction.guild.voice_client

        embed = Embed(title=":clock: History:")


        prev_track_label = []
        def enumerate_history_queue(queue):
            for idx, track in enumerate(queue[:9]):
                title = track.title
                if len(track.title) > 35:
                    title = f"{title[:32]} ..."
                prev_track_label.append(
                    f" [{title}]({track.uri}) | "
                    f"`{'🔴 Stream' if track.is_stream else datetime.timedelta(milliseconds=track.length)}`*"
                )

        enumerate_history_queue(player.queue.history)
        enumerate_history_queue(player.auto_queue.history)

        prl_len = len(prev_track_label)
        for idx, track in enumerate(prev_track_label):
            prev_track_label[idx] = f"*`{prl_len - idx + 1}.`" + track

        if prev_track_label:
            embed.add_field(
                name=f"Previous {len(prev_track_label)} Tracks:", value="\n".join(prev_track_label[:9]), inline=False
            )

        if player.current:
            if player.current:
                first_track: wavelink.Playable = player.current
                embed.add_field(
                    name="Now Playing:",
                    value=f'`1.` [{first_track.title}]({first_track.uri}) | `{"🔴 Stream" if first_track.is_stream else datetime.timedelta(milliseconds=first_track.length)}`',
                    inline=False,
                )

        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def loop(self, interaction: discord.Interaction):
        """Loop the current song"""

        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if not player.queue.mode == wavelink.QueueMode.loop:
            player.loop = wavelink.QueueMode.loop
            await interaction.response.send_message(
                embed=Embed(description="🔁 Track loop enabled"), delete_after=5
            )
        else:
            player.loop = wavelink.QueueMode.normal
            await interaction.response.send_message(
                embed=Embed(description="🔁 Track Loop disabled"), delete_after=5
            )


    @app_commands.command(name="loop_all")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def loop_all(self, interaction: discord.Interaction):
        """Loop the all queue"""

        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if not player.queue.mode == wavelink.QueueMode.loop_all:
            player.loop = wavelink.QueueMode.loop_all
            await interaction.response.send_message(
                embed=Embed(description="🔁 Queue loop enabled"), delete_after=5
            )
        else:
            player.loop = wavelink.QueueMode.normal
            await interaction.response.send_message(
                embed=Embed(description="🔁 Queue loop disabled"), delete_after=5
            )

    @app_commands.command(name="playlist")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def playlist(self, interaction: discord.Interaction, playlist_link: str):
        """Setup a playlist player for a YouTube playlist"""

        if not interaction.channel.permissions_for(self.user).send_messages:
            return await interaction.response.send_message(
                embed=Embed.error(description="Please allow me to send messages!"),
                ephemeral=True,
                delete_after=5,
            )

        # Check if the guild can have a new playlist
        if not await Database.Playlist.guild_limit(interaction.guild.id):
            return await interaction.response.send_message(
                embed=Embed.error(description="You can't have more than 10 playlists!")
            )

        if not re.match(PLAYLIST_REG, playlist_link):
            return await interaction.response.send_message(
                embed=Embed.error(description="The url is incorrect!"),
                ephemeral=True,
                delete_after=5,
            )

        playlist_id = re.search(PLAYLIST_ID, playlist_link).groups()[0]

        key = config.api.youtube.get("key")

        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/playlists?part=snippet&part=contentDetails&id={playlist_id}&key={key}"
        )
        if not r.ok:
            interaction.response.send_message(
                embed=Embed.error(description="Could not find the playlist!"), delete_after=5
            )

        r = r.json()
        if not r["items"]:
            return await interaction.response.send_message(
                embed=Embed.error(
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

        message = await interaction.channel.send(embed=embed)

        await Database.Playlist.create(message.id, message.guild.id, playlist_id)

        await message.add_reaction("<:back:990260521355862036>")
        await message.add_reaction("<:play:990260523692064798>")
        await message.add_reaction("<:next:990260522521858078>")
        await message.add_reaction("<:shuffle:990260524686139432>")

        await interaction.response.send_message(
            "Playlist successfully created!", ephemeral=True, delete_after=5
        )

    @app_commands.command(name="lavalinkinfo")
    @commands.guild_only()
    @commands.is_owner()
    async def lavalink_info(self, interaction: discord.Interaction):
        """Show lavalink info"""
        embed = Embed(title=f"**Wavelink:** `{wavelink.__version__}`", color=Colors.DEFAULT)

        embed.add_field(
            name="Server",
            value=f"Server Nodes: `{len(wavelink.Pool.nodes)}`\n"
            f"Voice Client Connected: `{len(self.client.voice_clients)}`\n",
            inline=False,
        )

        nodes = []
        for identifier, node in wavelink.Pool.nodes.items():
            nodes.append(f"`{identifier}`({len(node.players)})")

        embed.add_field(
            name=f"Nodes",
            value=f"{', '.join(nodes)}",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @filter.command(name="equalizer")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(sub_bass="16 - 60Hz(must be between -0.25 and 1.0)")
    @app_commands.describe(bass="60 - 250Hz (must be between -0.25 and 1.0)")
    @app_commands.describe(low_mids="250 - 500Hz (must be between -0.25 and 1.0)")
    @app_commands.describe(mids="500 - 2kHz (must be between -0.25 and 1.0)")
    @app_commands.describe(high_mids="2 - 4kHz (must be between -0.25 and 1.0)")
    @app_commands.describe(presence="4 - 6kHz (must be between -0.25 and 1.0)")
    @app_commands.describe(brillance="6 - 16kHz (must be between -0.25 and 1.0)")
    async def equalizer(
        self,
        interaction: discord.Interaction,
        sub_bass: float = None,
        bass: float = None,
        low_mids: float = None,
        mids: float = None,
        high_mids: float = None,
        presence: float = None,
        brillance: float = None,
        reset: bool = False,
    ):
        """An equalizer with 6 bands for adjusting the volume of different frequency."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        filters: wavelink.Filters = player.filters
        if reset:
            filters.equalizer.reset()
        else:
            bands_value = {
                0: sub_bass,
                2: bass,
                4: low_mids,
                6: mids,
                8: high_mids,
                10: brillance,
                12: presence,
            }
            filters: wavelink.Filters = player.filters
            equalizer = filters.equalizer

            for band, gain in bands_value.items():
                if not gain or not (gain >= -0.25 and gain <= 1.0):
                    return await interaction.response.send_message(
                        embed=Embed.error(description="Values must be between `-0.25` and `1.0`."),
                        ephemeral=True,
                        delete_after=5.0,
                    )

                equalizer.payload[band] = gain

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

        @filter.command(name="karaoke")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(level="The level of the effect (between 0.0 and 1.0).")
        @app_commands.describe(
            mono_level="The level of the mono effect (between 0.0 and 1.0)."
        )
        @app_commands.describe(
            filter_band="The frequency of the filter band in Hz (this defaults to 220.0)."
        )
        @app_commands.describe(
            filter_width="The width of the filter band (this defaults to 100.0)."
        )
        async def karaoke(
            self,
            interaction: discord.Interaction,
            level: float = None,
            mono_level: float = None,
            filter_band: float = None,
            filter_width: float = None,
        ):
            """Configure a Karaoke filter. This usually targets vocals, to sound like karaoke music."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            if (level and not (level <= 1.0 and level >= 0.0)) or (
                mono_level and not (mono_level <= 1.0 and mono_level >= 0.0)
            ):
                return await interaction.response.send_message(
                    embed=Embed.error(
                        "The level and mono_level values must be between `0.0` and `1.0`."
                    ),
                    ephemeral=True,
                    delete_after=5.0,
                )

            filters = player.filters
            filters.karaoke.set(level, mono_level, filter_band, filter_width)

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="timescale")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(speed="The speed of the audio (must be at least 0.0).")
        @app_commands.describe(pitch="The pitch of the audio (must be at least 0.0).")
        @app_commands.describe(rate="The rate of the audio (must be at least 0.0).")
        async def timescale(
            self,
            interaction: discord.Interaction,
            speed: float = None,
            pitch: float = None,
            rate: float = None,
        ):
            """Change the speed, pitch and rate of audio."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            if (
                (speed and not (speed <= 1.0 and speed >= 0.0))
                or (pitch and not (pitch <= 1.0 and pitch >= 0.0))
                or (rate and not (rate <= 1.0 and rate >= 0.0))
            ):
                return await interaction.response.send_message(
                    embed=Embed.error(description="Values must be between`0.0` and `1.0`."),
                    ephemeral=True,
                    delete_after=5.0,
                )

            filters = player.filters
            filters.timescale.set(speed, pitch, rate)

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="tremolo")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(
            frequency="The frequency of the tremolo effect (must be at least 0.0)."
        )
        @app_commands.describe(
            depth="The depth of the tremolo effect (between 0.0 and 1.0)."
        )
        async def tremolo(
            self,
            interaction: discord.Interaction,
            frequency: float = None,
            depth: float = None,
        ):
            """Tremolo oscillates the volume of the audio."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            if frequency and not (frequency >= 0.0 and frequency <= 2.0):
                return await interaction.response.send_message(
                    embed=Embed.error(
                        "Frequency value must be between`0.0` and `2.0`."
                    ),
                    ephemeral=True,
                    delete_after=5.0,
                )

            if depth and not (depth >= 0.0 and depth <= 1.0):
                return await interaction.response.send_message(
                    embed=Embed.error(
                        "Frequency value must be between`0.0` and `1.0` (this defaults to 0.5)."
                    ),
                    ephemeral=True,
                    delete_after=5.0,
                )

            filters = player.filters
            filters.tremolo.set(frequency, depth)

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="vibrato")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(
            frequency="The frequency of the tremolo effect (must be at least 0.0)."
        )
        @app_commands.describe(
            depth="The depth of the tremolo effect (between 0.0 and 1.0)."
        )
        async def vibrato(
            self,
            interaction: discord.Interaction,
            frequency: float = None,
            depth: float = None,
        ):
            """Vibrato oscillates the pitch of the audio."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            if frequency and not (frequency >= 0.0 and frequency <= 2.0):
                return await interaction.response.send_message(
                    embed=Embed.error(
                        "Frequency value must be between`0.0` and `2.0`."
                    ),
                    ephemeral=True,
                    delete_after=5.0,
                )

            if depth and not (depth >= 0.0 and depth <= 1.0):
                return await interaction.response.send_message(
                    embed=Embed.error(
                        "Frequency value must be between`0.0` and `1.0` (this defaults to 0.5)."
                    ),
                    ephemeral=True,
                    delete_after=5.0,
                )

            filters = player.filters
            filters.vibrato.set(frequency, depth)

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="distortion")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        async def distortion(
            self,
            interaction: discord.Interaction,
            sin_offset: Optional[float] = None,
            sin_scale: Optional[float] = None,
            cos_offset: Optional[float] = None,
            cos_scale: Optional[float] = None,
            tan_offset: Optional[float] = None,
            tan_scale: Optional[float] = None,
            offset: Optional[float] = None,
            scale: Optional[float] = None,
        ):
            """This applies sine, cosine and tangent distortion to the audio. Pretty hard to use."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            filters = player.filters
            filters.distortion.set(
                sin_offset,
                sin_scale,
                cos_offset,
                cos_scale,
                tan_offset,
                tan_scale,
                offset,
                scale,
            )

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="channel_mix")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(
            left_to_left="The amount of the left channel to mix into the left channel."
        )
        @app_commands.describe(
            left_to_right="The amount of the left channel to mix into the right channel."
        )
        @app_commands.describe(
            right_to_left="The amount of the right channel to mix into the left channel."
        )
        @app_commands.describe(
            right_to_right="The amount of the right channel to mix into the right channel."
        )
        async def channel_mix(
            self,
            interaction: discord.Interaction,
            left_to_left: float = None,
            left_to_right: float = None,
            right_to_left: float = None,
            right_to_right: float = None,
        ):
            """Channel mix filter (all at 0.5 => mono, ll=1.0 and rr=1.0 => stereo)."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            filters = player.filters
            filters.channel_mix.set(
                left_to_left, left_to_right, right_to_left, right_to_right
            )

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="low_pass")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        async def low_pass(self, interaction: discord.Interaction, smoothing: float):
            """High frequencies are suppressed, while low frequencies are passed through. (this defaults is 0.0)"""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            filters = player.filters
            filters.low_pass.set(smoothing)

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="rotation")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(rotation_hz="The rotation speed in Hz. (1.0 is fast)")
        async def rotation(
            self,
            interaction: discord.Interaction,
            rotation_hz: float = None,
        ):
            """Add a filter which can be used to add a rotating effect to audio."""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            if rotation_hz < 0.0:
                return await interaction.response.send_message(
                    embed=Embed.error(description="The rotation_hz value must be at least 0.0."),
                    ephemeral=True,
                    delete_after=5.0,
                )

            filters = player.filters
            filters.low_pass.set(rotation_hz)

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="The filter will be applied in a few seconds!"),
                delete_after=5.0,
            )

        @filter.command(name="volume")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        @app_commands.describe(
            volume="This defaults to 100 on creation. If the volume is outside 0 to 1000 it will be clamped."
        )
        async def volume(self, interaction: discord.Interaction, volume: int = 100):
            """Change the volume of the audio. (this apply to all users)"""
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            await player.set_volume(volume)

            await interaction.response.send_message(
                embed=Embed(description="Volume updated!"), delete_after=5.0
            )

        @filter.command(name="clear")
        @commands.guild_only()
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
        async def volume(self, interaction: discord.Interaction):
            player: wavelink.Player = interaction.guild.voice_client

            if not player:
                return

            filters = player.filters
            filters.reset()

            await player.set_filters(filters)

            await interaction.response.send_message(
                embed=Embed(description="Filters clear!"), delete_after=5.0
            )
