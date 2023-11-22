from .music import Music
from .music_event import MusicEvent
from .playlist_event import PlaylistEvent


async def setup(bot):
    await bot.add_cog(Music(bot))
    await bot.add_cog(MusicEvent(bot))
    await bot.add_cog(PlaylistEvent(bot))
