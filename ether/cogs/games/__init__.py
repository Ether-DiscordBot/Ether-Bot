from .games import Games


async def setup(bot):
    await bot.add_cog(Games(bot))
