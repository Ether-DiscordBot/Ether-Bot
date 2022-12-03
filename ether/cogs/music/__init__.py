from .music import Music
from .playlist import Playlist


def setup(bot):
    bot.add_cog(Music(bot))
    bot.add_cog(Playlist(bot))
