from .dnd import DnD


def setup(bot):
    bot.add_cog(DnD(bot))
