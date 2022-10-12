from .event import Event


def setup(bot):
    bot.add_cog(Event(bot))
