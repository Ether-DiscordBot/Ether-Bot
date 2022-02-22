from random import choice

import discord
from discord import Embed, User
from discord.ext import commands


class Fun(commands.Cog):
    HEIGHT_BALL_ANSWERS = [
        [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may reply on it.",
            "As I see it, yes.",
            "Most likely",
            "Outlook good.",
            "Yes.",
            "Signs point to yes."
        ],
        [
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again."
        ],
        [
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
    ]

    def __init__(self, client):
        self.fancy_name = "Fun"
        self.client = client

    @commands.command(name="8ball", aliases=["8-ball"])
    async def height_ball(self, ctx: commands.Context, question: str = None):
        """
        Based on the standard Magic 8 Ball.
        """

        if not question:
            return await ctx.reply(f"What would you ask to the Magic 8-Ball ?",
                                   allowed_mentions=discord.AllowedMentions.none())

        await ctx.send(f"🎱 {choice(choice(self.HEIGHT_BALL_ANSWERS))}")

    @commands.command(name="say", aliases=["tell"])
    async def say(self, ctx: commands.Context, *args):
        """
        Say what something the user want to.
        """

        if args[len(args)-1] in ("--hide", "-h"):
            hide = True
            args = list(args)
            args.pop(len(args)-1)
        else:
            hide = False

        text = " ".join(args)

        if len(text) <= 0:
            return await ctx.reply(f"What would you like me to say ?",
                                   allowed_mentions=discord.AllowedMentions.none())

        if hide:
            await ctx.message.delete()
        await ctx.send(text)
