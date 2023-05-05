import random
import discord

from discord.ext import commands

from ether.core.constants import Other
from ether.core.db.client import Playlist
from ether.core.voice_client import EtherPlayer


class PlaylistEvent(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    async def ensure_voice(self, payload):
        """This check ensures that the bot and command author are in the same voicechannel."""
        if not payload.member.voice or not payload.member.voice.channel:
            return

        guild = self.client.get_guild(payload.guild_id)
        player: EtherPlayer = guild.voice_client

        if not player:
            await payload.member.voice.channel.connect(cls=EtherPlayer)

            player: EtherPlayer = guild.voice_client
            setattr(player, "channel", payload.channel_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
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

            player: EtherPlayer = payload.member.guild.voice_client
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

            load_playlist = await player.fetch_tracks(playlist_link)
            
            if load_playlist:
                shuffle = emoji.id == 990260524686139432
                if shuffle:
                    random.shuffle(load_playlist.tracks)
                tracks = load_playlist.tracks
                if len(tracks) > 1:
                    player.queue.extend(tracks[1:])

                new_embed = message.embeds[0].copy()

                # Update tracks count
                if not new_embed.fields[0].value.startswith(
                    str(len(load_playlist.tracks))
                ):
                    new_embed.set_field_at(
                        0,
                        name="Tracks",
                        value=f"{str(len(load_playlist.tracks))} tracks",
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

            await player.play(load_playlist.tracks[0])
        elif emoji.id == 990260521355862036:  # back
            pass
        elif emoji.id == 990260522521858078:  # skip
            player = self.client.lavalink.player_manager.get(payload.guild_id)
            if not player:
                return

            await player.skip()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        p_message = await Playlist.from_id(payload.message_id)
        if p_message:
            await p_message.delete()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if self.client.id != Other.MAIN_CLIENT_ID:
            return

        playlists = await Playlist.from_guild(guild.id)
        if playlists:
            await playlists.delete()
