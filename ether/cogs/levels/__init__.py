from .levels import Levels


async def setup(bot):
    await bot.add_cog(Levels(bot))
