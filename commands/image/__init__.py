from .image import Image


def setup(bot):
    bot.add_cog(Image(bot))
