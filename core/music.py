import lavalink

from discord import Embed


def get_client(guild_id):
    """
    :param guild_id: the guild id
    :return: lavalink.Player or None
    """

    try:
        player = lavalink.get_player(guild_id=guild_id)
    except:
        player = None

    return player


async def user_is_in_client_channel(ctx):
    """
    Return if a user is in the same voice channel as the bot.
    :param ctx: context
    :param music_client: lavalink.Player
    :return: True or False
    """

    music_client = get_client(ctx.guild.id)

    if music_client is None:
        await join_voice_channel(ctx)
        return True

    if music_client and music_client.channel:
        if ctx.author.voice and ctx.author.voice.channel == music_client.channel:
            return True

    return False


async def join_voice_channel(ctx):
    """
    :param ctx: context
    :return: String or lavalink.Player
    """

    music_client = get_client(ctx.guild.id)

    if music_client and music_client.channel:
        return "I'm already connected in a voice channel."

    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        return await lavalink.connect(voice_channel)
    else:
        return "You must be connected to a voice channel."


async def play(ctx):
    """
    :param ctx: context
    :return: True or None
    """

    music_client = get_client(ctx.guild.id)

    if music_client is None:
        music_client = await join_voice_channel(ctx)

    if music_client.current is None and music_client.channel:
        await music_client.play()

        return True
    else:
        return


async def next_track(ctx):
    """
    :param ctx: context
    :return: True or None
    """

    music_client = get_client(ctx.guild.id)

    if music_client and music_client.is_playing and music_client.channel:
        await music_client.skip()
        return True
    else:
        return


async def stop(ctx):
    """
    :param ctx: context
    :return: True or None
    """

    music_client = get_client(ctx.guild.id)

    if music_client and music_client.is_playing and music_client.channel:
        await music_client.current.start_message.delete()
        await music_client.stop()

        return True
    else:
        return


async def pause(ctx):
    """
    :param ctx: context
    :return: True or None
    """

    music_client = get_client(ctx.guild.id)

    if music_client.channel:
        await music_client.pause()

        return True
    else:
        return False


async def leave(ctx):
    """
    :param ctx: context
    :return: True or False
    """
    music_client = get_client(ctx.guild.id)

    if music_client.channel:
        await music_client.disconnect()


async def add_track_to_queue(ctx, track):
    """
    :param ctx: context
    :param track: the track to add in the queue
    :return: True
    """

    music_client = get_client(ctx.guild.id)

    if music_client.channel:
        music_client = get_client(ctx.guild.id)

        track.channel = ctx.channel

        music_client.add(ctx.author, track)

        if music_client.current:
            embed = Embed(description="Queued [{0.title}]({0.uri})".format(track))
            return await ctx.send(embed=embed)
        else:
            return
    else:
        return


async def search_track(ctx, arg):
    """
    :param ctx: context
    :param arg: argument (url or keyword.s)
    :return: Track or None
    """

    music_client = get_client(ctx.guild.id)

    if music_client.channel:
        result = await music_client.search_yt(arg)
        return result.tracks[0]
    else:
        return


def get_queue(ctx):
    """
    :param ctx: context
    :return: lavalink.Player.queue or None
    """

    music_client = get_client(ctx.guild.id)

    if music_client is not None:
        return music_client.queue
    else:
        return
