from .event import Event


async def setup(bot):
    await bot.add_cog(Event(bot))
