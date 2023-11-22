from .birthdays import Birthday


async def setup(bot):
    await bot.add_cog(Birthday(bot))
