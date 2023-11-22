from .reactions import Reactions


async def setup(bot):
    await bot.add_cog(Reactions(bot))
