import random

from discord.ext import commands
import wavelink

from ether.cogs.music.music import Player
from ether.core.db.client import Guild, Playlist


class Playlist(commands.Cog):
    def __init__(self) -> None:
        pass

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
