from .steam import Steam


def setup(bot):
    bot.add_cog(Steam(bot))
