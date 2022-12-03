from .music import Music
from .playlist import PlaylistCog


def setup(bot):
    bot.add_cog(Music(bot))
    bot.add_cog(PlaylistCog(bot))
