from .remix import Remix


async def setup(bot):
    await bot.add_cog(Remix(bot))
