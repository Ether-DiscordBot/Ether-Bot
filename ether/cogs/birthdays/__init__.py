from .birthdays import Birthday


def setup(bot):
    bot.add_cog(Birthday(bot))
