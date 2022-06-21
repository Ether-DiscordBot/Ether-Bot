from .nasa import Nasa


def setup(bot):
    bot.add_cog(Nasa(bot))
