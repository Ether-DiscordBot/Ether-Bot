from .dnd import DnD


async def setup(bot):
    await bot.add_cog(DnD(bot))
