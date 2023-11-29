import random

import discord
import wavelink
from discord.ext import commands

from ether.core.constants import Other
from ether.core.db.client import Playlist
from ether.core.logging import log


class PlaylistEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    async def ensure_voice(self, payload: discord.RawReactionActionEvent):
        """This check ensures that the bot and command author are in the same voicechannel."""
        if not payload.member.voice or not payload.member.voice.channel:
            return

        guild = payload.member.guild
        player = guild.voice_client

        if not player:
            await payload.member.voice.channel.connect(cls=wavelink.Player)

            player = guild.voice_client
            setattr(player, "channel", payload.channel_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:
            return

        playlist = await Playlist.from_id(payload.message_id)
        if not playlist:
            return

        await self.ensure_voice(payload)

        channel = payload.member.guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = [r for r in message.reactions if r.emoji.name == payload.emoji.name][
            0
        ]

        await reaction.remove(payload.member)

        emoji = payload.emoji
        if emoji.id in (990260523692064798, 990260524686139432):  # Play
            if not payload.member.voice:
                return

            player: wavelink.Player = payload.member.guild.voice_client
            if not player:
                return

            await payload.member.guild.change_voice_state(
                channel=payload.member.voice.channel,
                self_mute=False,
                self_deaf=True,
            )

            if len(player.queue) > 0:
                return

            playlist_link = (
                f"https://www.youtube.com/playlist?list={playlist.playlist_id}"
            )

            load_playlist: wavelink.Playlist = await wavelink.Pool.fetch_tracks(playlist_link)

            if load_playlist:
                shuffle = emoji.id == 990260524686139432
                if shuffle:
                    random.shuffle(load_playlist.tracks)
                await player.queue.put_wait(load_playlist.tracks[1:])

                await player.play(player.queue.get())

                new_embed = message.embeds[0].copy()

                # Update tracks count
                if not new_embed.fields[0].value.startswith(
                    str(len(load_playlist.tracks))
                ):
                    new_embed.set_field_at(
                        0,
                        name="Tracks",
                        value=f"{len(load_playlist)} tracks",
                    )

                # Update title
                if message.embeds[0].title != f"[Playlist] {load_playlist.name}":
                    new_embed.title = f"[Playlist] {load_playlist.name}"

                # Push changes
                try:
                    if message.embeds[0].to_dict() != new_embed.to_dict():
                        await message.edit(embed=new_embed)
                except discord.errors.Forbidden:
                    pass
        elif emoji.id == 990260521355862036:  # back
            player: wavelink.Player = payload.member.guild.voice_client

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
                return

            await player.play(track, replace=True)
        elif emoji.id == 990260522521858078:  # skip
            player: wavelink.Player = payload.member.guild.voice_client
            if not player:
                return

            # await player.skip(force=True)
            await player.play(player.queue.get())

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        p_message = await Playlist.from_id(payload.message_id)
        if p_message:
            await p_message.delete()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if self.client.user.id != Other.MAIN_CLIENT_ID:
            return

        if playlists := Playlist.from_guild(guild.id):
            await playlists.delete()
