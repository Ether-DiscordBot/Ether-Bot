from discord import ApplicationCommand, Embed, Message, SlashCommandGroup
from discord.ext import commands

from ether.core.db import Database
from ether.core.db.client import ReactionRole


class Reactions(commands.Cog, name="reaction"):
    def __init__(self, client) -> None:
        self.fancy_name = "Reactions"
        self.client = client
    
    reactions = SlashCommandGroup("reactions", "Reactions roles commands!")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot: return

        message_id = payload.message_id
        emoji = payload.emoji.name

        reaction = await ReactionRole.from_id(message_id)
        if reaction:
            matchs_emojis = [e for e in reaction.options if e.reaction == emoji]
            if matchs_emojis[0]:
                role = payload.member.guild.get_role(matchs_emojis[0].role_id)
                await payload.member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        emoji = payload.emoji.name

        reaction = await ReactionRole.from_id(message_id)
        if reaction:
            matchs_emojis = [e for e in reaction.options if e.reaction == emoji]
            if matchs_emojis[0]:
                guild = self.client.get_guild(payload.guild_id)
                role = guild.get_role(matchs_emojis[0].role_id)

                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        r_message = await ReactionRole.from_id(payload.message_id)
        if r_message:
            await r_message.delete()
    
    # @reactions.command()
    # @commands.is_owner()
    # async def test(self, ctx: ApplicationCommand):
    #     embed = Embed(title="Reactions roles message", description="There is a reactions roles message.")
    #     msg: Message = await ctx.channel.send(embed=embed)
        
    #     await msg.add_reaction("🚀")
    #     await msg.add_reaction("💎")
        
    #     options = [Database.ReactionRole.ReactionRoleOption.create(role_id=697741680409051198, reaction="🚀"),
    #                Database.ReactionRole.ReactionRoleOption.create(role_id=697741680409051198, reaction="💎")]
    #     await Database.ReactionRole.create(msg.id, options)
        
    #     await ctx.respond("✅ Done !", delete_after=5)