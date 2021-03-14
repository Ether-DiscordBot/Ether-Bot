from abc import abstractmethod

from discord.ext import commands

from core.music import *


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

        lavalink.register_event_listener(
            self.lavalink_event_handler
        )

    @abstractmethod
    async def lavalink_event_handler(self, player: lavalink.Player, event_type: lavalink.LavalinkEvents, extra):

        if event_type == lavalink.LavalinkEvents.TRACK_START:
            track = player.current
            embed = Embed(description="▶️ **Now playing** [{0.title}]({0.uri}) !".format(track))
            message = await track.channel.send(embed=embed)
            track.start_message = message

        if event_type == lavalink.LavalinkEvents.TRACK_END:

            if extra == lavalink.TrackEndReason.FINISHED:
                track = player.current
                await track.start_message.delete()

            if len(player.queue):
                await player.stop()
                print(player.is_playing)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def join(self, ctx):
        response = await join_voice_channel(ctx)

        if type(response) == str:
            return await ctx.send(embed=Embed(description=response))
        else:
            return await ctx.message.add_reaction("👌")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leave(self, ctx):
        if await leave(ctx) is not None:
            return await ctx.message.add_reaction("👋")
        else:
            return

    @commands.command()
    async def stop(self, ctx):
        if await stop(ctx) is not None:
            return await ctx.message.add_reaction("🛑")
        else:
            return

    @commands.command()
    async def skip(self, ctx):
        if await next_track(ctx) is not None:
            return await ctx.message.add_reaction("⏭️")
        else:
            return

    @commands.command(aliases=['p'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, arg):
        global embed

        prefix_len = len(await self.client.get_prefix(ctx.message))
        if arg:
            if ctx.author.voice and ctx.author.voice.channel:
                is_in_client_channel = await user_is_in_client_channel(ctx)
                if is_in_client_channel:
                    await add_track_to_queue(ctx, await search_track(ctx=ctx, arg=arg))
                    await play(ctx)
                    return
                else:
                    embed = Embed(description="You must be connected in the same voice channel as the bot.")
            else:
                embed = Embed(description="You must be connected to a voice channel.")

            return await ctx.send(embed=embed)
        else:
            return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        queue = get_queue(ctx)

        if queue is None:
            return
        else:
            music_client = get_client(ctx.guild.id)

            message = "# Current track: \n" \
                      "1.  {0.title} [{1}]\n \n".format(music_client.current, lavalink.utils.format_time(music_client.current.length))

            if len(queue) > 0:
                message += "# Queue: \n"
                index = 1
                for track in queue:
                    index += 1
                    if index == 10:
                        if len(queue) > 10:
                            message += "{0}. {1.title} [{2}]\n...".format(index, track,
                                                                          lavalink.utils.format_time(track.length))
                        else:
                            message += "{0}. {1.title} [{2}]\n".format(index, track,
                                                                          lavalink.utils.format_time(track.length))
                        break
                    message += "{0}.  {1.title} [{2}]\n".format(index, track, lavalink.utils.format_time(track.length))

            return await ctx.send(f"```glsl\n {message}```")


def setup(client):
    client.add_cog(Music(client))
