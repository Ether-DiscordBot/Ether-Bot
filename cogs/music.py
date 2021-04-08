from discord.ext import commands
from discord import Embed

import lavalink


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def join(self, ctx):
        response = await self.client.musicCmd.join_voice_channel(ctx)

        if type(response) == str:
            return await ctx.send(embed=Embed(description=response))
        else:
            return await ctx.message.add_reaction("👌")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leave(self, ctx):
        if await self.client.musicCmd.leave(ctx) is not None:
            return await ctx.message.add_reaction("👋")
        else:
            return

    @commands.command()
    async def stop(self, ctx):
        if await self.client.musicCmd.stop(ctx) is not None:
            return await ctx.message.add_reaction("🛑")
        else:
            return

    @commands.command()
    async def skip(self, ctx):
        if await self.client.musicCmd.next_track(ctx) is not None:
            return await ctx.message.add_reaction("⏭️")
        else:
            return

    @commands.command(aliases=['p'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def play(self, ctx, *args):
        if ctx.author.voice and ctx.author.voice.channel:
            is_in_client_channel = await self.client.musicCmd.user_is_in_client_channel(ctx)
            if is_in_client_channel:
                if args:
                    track = await self.client.musicCmd.search_track(ctx=ctx, arg=args[0], args=args)
                    if track is not None:
                        await self.client.musicCmd.add_track_to_queue(ctx, track, arg=args[0])
                        return await self.client.musicCmd.play(ctx)
                    else:
                        embed = Embed(description="Music not found", color=0xe74c3c)
                        return await ctx.send(embed=embed)
                else:
                    return await self.client.musicCmd.play(ctx)
            else:
                embed = Embed(description="You must be connected in the same voice channel as the bot.")
        else:
            embed = Embed(description="You must be connected to a voice channel.")

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def queue(self, ctx):
        queue = self.client.musicCmd.get_queue(ctx)

        if ctx.author.voice and ctx.author.voice.channel:
            is_in_client_channel = await self.client.musicCmd.user_is_in_client_channel(ctx)
            if is_in_client_channel:
                music_client = self.client.musicCmd.get_client(ctx.guild.id)
                if music_client.current is None and queue is None:
                    return
                else:
                    message = "# Current track: \n" \
                              "1.  {0.title} [{1}]\n".format(music_client.current, lavalink.utils
                                                             .format_time(music_client.current.length))
                    if len(queue) > 0:
                        message += "\n# Queue: \n"
                        index = 1
                        for track in queue:
                            index += 1
                            if index == 10:
                                if len(queue) > 10:
                                    message += "{0}. {1.title} [{2}]\n..." \
                                        .format(index, track, lavalink.utils.format_time(track.length))
                                else:
                                    message += "{0}. {1.title} [{2}]\n" \
                                        .format(index, track, lavalink.utils.format_time(track.length))
                                break
                            message += "{0}.  {1.title} [{2}]\n" \
                                .format(index, track, lavalink.utils.format_time(track.length))

                    return await ctx.send(f"```glsl\n {message}```")
            else:
                embed = Embed(description="You must be connected in the same voice channel as the bot.")
        else:
            embed = Embed(description="You must be connected to a voice channel.")

        return await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx):
        await self.client.musicCmd.pause(ctx, True)

    @commands.command()
    async def resume(self, ctx):
        await self.client.musicCmd.pause(ctx, False)


def setup(client):
    client.add_cog(Music(client))
