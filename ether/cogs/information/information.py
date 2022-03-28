from discord import Embed, Member
from discord.ext import commands
from humanize import naturaldate, naturalsize


class Information(commands.Cog, name="information"):
    def __init__(self, client):
        self.fancy_name = "Information"
        self.client = client
    
    @commands.command(name="user", alises=["member"])
    async def user(self, ctx, *, member: Member = None):
        member = member if member else ctx.author
        avatar = member.avatar_url_as()
        
        embed = Embed(description=f"**ID:** {member.id}")
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=avatar, url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Account creation date", value=naturaldate(member.created_at), inline=False)
        embed.add_field(name="Server join date", value=naturaldate(member.joined_at), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="server", aliases=["guild"])
    async def server(self, ctx):
        guild = ctx.guild
        
        embed = Embed(title="", description=f"**ID:** {guild.id}")
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name="Server boost", value=f"Level {guild.premium_tier}/3")
        embed.add_field(name="Members", value=f"{guild.member_count}/{guild.max_members} ({guild.approximate_presence_count} online)", inline=False)
        embed.add_field(name="Server creation date", value=naturaldate(guild.created_at), inline=False)
        embed.add_field(name="Additional informations", value=f"\t**Emoji:** {len(guild.emojis)}/{guild.emoji_limit}\n"
                        f"\t**Sticker:** {len(guild.stickers)}/{guild.sticker_limit}\n"
                        f"\t**Filesize:** {naturalsize(guild.file)}"
                        , inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["pp"])
    async def avatar(self, ctx):
        user = ctx.message.mentions[0] if ctx.message.mentions else ctx.message.author
        embed = Embed(
            description="**{0.display_name}'s** [avatar]({0.avatar_url}):".format(user)
        ).set_image(url=user.avatar_url_as(format="png", size=256))
        return await ctx.channel.send(embed=embed)