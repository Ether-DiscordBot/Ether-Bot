import datetime
import random
import re
from typing import cast

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

from .filters import Filters

PLAYLIST_REG = re.compile(
    r"^(?:http:\/\/|https:\/\/)?(?:www\.)?youtube\.com\/playlist\?list(?:\S+)?$"
)
PLAYLIST_ID = re.compile(r"[&?]list=([^&]+)")
URL_REG = re.compile(
    r"(?:https:\/\/|http:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*"
)


class Music(commands.Cog, group_name="music"):
    def __init__(self, client):
        self.client = client
        self.help_icon = Emoji.MUSIC
        self.youtube_api_key = config.api.youtube.get("key")

        self.tape_in = open("ether/assets/sfx/tape_in.mp3", "rb").read()

    music = app_commands.Group(
        name="music", description="Tthhee Ppaarrttyy"
    )

    filter = Filters(parent=music)

    async def interaction_check(self, interaction: discord.Interaction):
        """Command before-invoke handler."""

        exceptions = ("playlist", "queue", "lavalinkinfo")
        if interaction.command.name in exceptions:
            return True

        guild_check = interaction.guild != None

        return await self.ensure_voice(interaction) if guild_check else guild_check

    async def ensure_voice(self, interaction: discord.Interaction) -> bool:
        """This check ensures that the bot and command author are in the same voicechannel."""

        should_connect = interaction.command.name in ("play", "join")

        if (
            not interaction.user.voice
            or not interaction.user.voice.channel
        ):
            await interaction.response.send_message(
                embed=Embed.error(description="Join a voicechannel first."),
                ephemeral=True,
                delete_after=5,
            )
            return False

        player: wavelink.Player = interaction.guild.voice_client

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
        if player := cast(wavelink.Player, interaction.guild.voice_client):
            if not hasattr(player, "home"):
                player.home = interaction.channel
            elif player.home != interaction.channel:
                await interaction.response.send_message(Embed.error(description=f"You can only play songs in {player.home.mention}, as the player has already started there."), ephemeral=True, delete_after=5)

        return True

    @app_commands.command(name="play")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(
        source=[
            Choice(name="YouTube", value="ytsearch"),
            Choice(name="YouTube Music", value="ytmsearch"),
            Choice(name="SoundCloud", value="scsearch"),
            Choice(name="Spotify", value="spsearch"),
            Choice(name="Deezer", value="dzsearch")
        ]
    )
    async def play(
        self,
        interaction: discord.Interaction,
        *,
        query: str,
        shuffle: bool = False,
        source: Choice[str] = "ytsearch",
        auto_play: bool = True,
    ):
        """Play a song or a playlist from YouTube, YT Music or Soundcloud

        query:
            The song to search or play
        """

        return await self.music_play.callback(
            self,
            interaction=interaction,
            query=query,
            shuffle=shuffle,
            source=source,
            auto_play=auto_play
        )



    @music.command(name="play")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(
        source=[
            Choice(name="YouTube", value="ytsearch"),
            Choice(name="YouTube Music", value="ytmsearch"),
            Choice(name="SoundCloud", value="scsearch"),
            Choice(name="Spotify", value="spsearch"),
            Choice(name="Deezer", value="dzsearch")
        ]
    )
    async def music_play(
        self,
        interaction: discord.Interaction,
        *,
        query: str,
        shuffle: bool = False,
        source: Choice[str] = "ytsearch",
        auto_play: bool = True,
    ):
        """Play a song or a playlist from YouTube, YT Music or Soundcloud

        query:
            The song to search or play
        """
        await interaction.response.defer(thinking=True)

        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore

        if not player:
            return

        if auto_play:
            player.autoplay = wavelink.AutoPlayMode.enabled

        if hasattr(source, "value"):
            source = source.value

        try:
            tracks = await wavelink.Playable.search(query, source=source)

            if not tracks:
                return await interaction.response.edit_original_response(
                    embed=Embed.error(description="No tracks were found!")
                )

            if isinstance(tracks, wavelink.Playlist):
                playlist_tracks = tracks.tracks
                if shuffle:
                    random.shuffle(playlist_tracks)

                added: int = await player.queue.put_wait(playlist_tracks)

                await interaction.edit_original_response(
                    embed=Embed(
                        description=f"**[{tracks.name}]({query})** - {len(added)} tracks",
                        color=Colors.DEFAULT,
                    )
                )
            else:
                track: wavelink.Playable = tracks[0]
                await player.queue.put_wait(track)
                await interaction.edit_original_response(
                    embed=Embed(
                        description=f"Track added to queue: **[{track.title}]({track.uri})**",
                        color=Colors.DEFAULT,
                    )
                )

            if not player.playing:
                await player.play(player.queue.get())
        except wavelink.exceptions.LavalinkLoadException as err:
            await interaction.edit_original_response(
                embed=Embed.error(
                    title="Failed to load tracks",
                    description=err.error
                )
            )

            log.warning(f"Failed to load tracks with query: {query}, error={err.error}")


    @music.command(name="stop")
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
        await player.skip(force=True)

        await interaction.response.send_message(
            embed=Embed(description="🛑 Stopped"), delete_after=5
        )
        await player.disconnect()

    @music.command(name="pause")
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

    @music.command(name="resume")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def resume(self, interaction: discord.Interaction):
        """Resume the current song"""
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return

        if not player.current:
            await interaction.response.send_message(
                embed=Embed.error(description="I am not currently playing anything!"),
                delete_after=5,
            )
            return

        if not player.paused:
            await interaction.response.send_message(
                embed=Embed.error(description="I am not paused!"), delete_after=5
            )
            return

        await player.pause(False)
        await interaction.response.send_message(
            embed=Embed(description="⏸️ Resume"), delete_after=5
        )

    @music.command(name="skip")
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

    @music.command(name="shuffle")
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

    @music.command(name="queue")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: discord.Interaction):
        """Show the current queue"""
        player: wavelink.Player = interaction.guild.voice_client

        embed = Embed(title=":notes: Queue:")

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

    @music.command(name="autoplay")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def autoplay(self, interaction: discord.Interaction, *, enabled: bool = None):
        "Toggle the auto play"
        player: wavelink.Player = interaction.guild.voice_client

        if enabled is None:
            enabled = player.autoplay != wavelink.AutoPlayMode.enabled

        if enabled:
            player.autoplay = wavelink.AutoPlayMode.enabled
            return await interaction.response.send_message(Embed(description="✅ Auto play enabled"))

        player.autoplay = wavelink.AutoPlayMode.disabled
        return await interaction.response.send_message(Embed(description="✅ Auto play disabled"))

    @music.command(name="back")
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

    @music.command(name="history")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def history(self, interaction: discord.Interaction):
        """Show the current queue"""
        player: wavelink.Player = interaction.guild.voice_client

        embed = Embed(title=":clock: History:")


        prev_track_label = []
        def enumerate_history_queue(queue):
            for _idx, track in enumerate(queue[:len(queue)-1]):
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
            prev_track_label[idx] = f"*`{prl_len - idx + 1}.`{track}"

        if prev_track_label:
            embed.add_field(
                name=f"{len(prev_track_label)} Previous tracks:", value="\n".join(prev_track_label[:9]), inline=False
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

    @music.command(name="loop")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def loop(self, interaction: discord.Interaction):
        """Loop the current song"""

        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if player.queue.mode != wavelink.QueueMode.loop:
            player.loop = wavelink.QueueMode.loop
            await interaction.response.send_message(
                embed=Embed(description="🔁 Track loop enabled"), delete_after=5
            )
        else:
            player.loop = wavelink.QueueMode.normal
            await interaction.response.send_message(
                embed=Embed(description="🔁 Track Loop disabled"), delete_after=5
            )


    @music.command(name="loop_all")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def loop_all(self, interaction: discord.Interaction):
        """Loop the all queue"""

        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if player.queue.mode != wavelink.QueueMode.loop_all:
            player.loop = wavelink.QueueMode.loop_all
            await interaction.response.send_message(
                embed=Embed(description="🔁 Queue loop enabled"), delete_after=5
            )
        else:
            player.loop = wavelink.QueueMode.normal
            await interaction.response.send_message(
                embed=Embed(description="🔁 Queue loop disabled"), delete_after=5
            )


    @music.command(name="lyrics")
    @commands.guild_only()
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def lyrics(self, interaction: discord.Interaction):
        """Get the lyrics of the current track"""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if not player.current:
            return await interaction.response.send_message(
                embed=Embed.error(description="I am not currently playing anything!"),
                delete_after=5,
            )

        await interaction.response.defer(thinking=True)

        async def lyrics_send(path: str):
            try:
                return await player.node.send("GET", path=path)
            except wavelink.exceptions.LavalinkException as _:
                return None

        lyrics = None
        lyrics = await lyrics_send(path=f"v4/sessions/{player.node.session_id}/players/{player.guild.id}/lyrics")

        if lyrics is None:
            tracks = await lyrics_send(path=f"v4/lyrics/search/{player.current.title} - {player.current.author}")

            if tracks:
                for track in tracks[:2]:
                    lyrics = await lyrics_send(path=f"v4/lyrics/{track['videoId']}")
                    if lyrics != None and ('lines' in lyrics['track'] or 'text' in lyrics):
                        break

        if lyrics is None and ('lines' in lyrics or 'text' in lyrics):
            return await interaction.edit_original_response(
                    embed=Embed.error(
                        description="Sorry, we haven't found any lyrics for this music.",
                    )
                )

        text = ""

        if lyrics['type'] == "timed":
            for line in lyrics['lines']:
                range = line['range']
                if range['start'] < player.position and range['end'] > player.position:
                    text += "> "
                else:
                    text += "  "

                text += line['line'] + "\n"

                if len(text) >= 1900:
                    text += "  ..."
                    break
        else:
            text = lyrics['text'][:1900]

        return await interaction.edit_original_response(
            content=f"""
```md
## {lyrics['track']['title']} - {lyrics['track']['author']}

{text}
```
"""
        )



    @music.command(name="playlist")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def playlist(self, interaction: discord.Interaction, playlist_link: str):
        """Setup a playlist player for a YouTube playlist"""

        if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
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
