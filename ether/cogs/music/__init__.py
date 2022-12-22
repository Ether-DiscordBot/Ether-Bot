from .music import Music
from .music_event import MusicEvent
from .playlist_event import PlaylistEvent


def setup(bot):
    bot.add_cog(Music(bot))
    bot.add_cog(MusicEvent(bot))
    bot.add_cog(PlaylistEvent(bot))
