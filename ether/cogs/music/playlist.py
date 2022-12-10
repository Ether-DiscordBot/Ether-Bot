import random
import discord

from discord.ext import commands
import wavelink

from ether.cogs.music.music import Player
from ether.core.constants import Other
from ether.core.db.client import Guild, Playlist


class PlaylistCog(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

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

            wevelink_playlist = await vc.node.get_playlist(
                cls=wavelink.YouTubePlaylist, identifier=playlist.playlist_link
            )
            if wevelink_playlist:
                shuffle = emoji.id == 990260524686139432
                if shuffle:
                    random.shuffle(wevelink_playlist.tracks)
                for t in wevelink_playlist.tracks:
                    vc.queue.put(t)

                new_embed = message.embeds[0].copy()
                # Update tracks count
                if not new_embed.fields[0].value.startswith(
                    str(len(wevelink_playlist.tracks))
                ):
                    new_embed.set_field_at(
                        0,
                        name="Tracks",
                        value=f"{str(len(wevelink_playlist.tracks))} tracks",
                    )

                # Update title
                if message.embeds[0].title != f"[Playlist] {wevelink_playlist.name}":
                    new_embed.title = f"[Playlist] {wevelink_playlist.name}"

                # Push changes
                try:
                    if message.embeds[0].to_dict() != new_embed.to_dict():
                        await message.edit(embed=new_embed)
                except discord.errors.Forbidden:
                    pass

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
