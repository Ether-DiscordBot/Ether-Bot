from .steam import Steam


async def setup(bot):
    await bot.add_cog(Steam(bot))
