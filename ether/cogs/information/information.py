from discord import Embed, Member
from discord.ext import commands
from humanize import naturaldate


class Information(commands.Cog, name="information"):
    def __init__(self, client):
        self.fancy_name = "Information"
        self.client = client
    
    @commands.command(name="user")
    async def user(self, ctx, *, member: Member = None):
        member = member if member else ctx.author
        avatar = member.avatar_url_as()
        
        embed = Embed(description=f"**ID:** {member.id}")
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=avatar, url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Account creation date", value=naturaldate(member.created_at), inline=False)
        embed.add_field(name="Server join date", value=naturaldate(member.joined_at), inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["pp"])
    async def avatar(self, ctx):
        user = ctx.message.mentions[0] if ctx.message.mentions else ctx.message.author
        embed = Embed(
            description="**{0.display_name}'s** [avatar]({0.avatar_url}):".format(user)
        ).set_image(url=user.avatar_url_as(format="png", size=256))
        return await ctx.channel.send(embed=embed)