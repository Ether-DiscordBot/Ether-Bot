from discord import ApplicationCommand, Message, NotFound, Role, SlashCommandGroup
from discord.errors import HTTPException
from discord.ext import commands
from ether.core.i18n import _

from ether.core.db.client import Database, ReactionRole
from ether.core.constants import Emoji
from ether.core.utils import EtherEmbeds


class Reactions(commands.Cog, name="reaction"):
    def __init__(self, client) -> None:
        self.help_icon = Emoji.REACTIONS
        self.client = client

    reactions = SlashCommandGroup("reactions", "Reactions roles commands!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

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

    @reactions.command()
    @commands.is_owner()
    async def add(
        self, ctx: ApplicationCommand, message_id: str, emoji: str, role: Role
    ):
        try:
            msg: Message = await ctx.fetch_message(message_id)
        except NotFound:
            return await ctx.respond(
                embed=EtherEmbeds.error(_("Message not found!")),
                ephemeral=True,
                delete_after=5,
            )

        try:
            await msg.add_reaction(emoji)

            options = [
                Database.ReactionRole.ReactionRoleOption.create(
                    role_id=role.id, reaction=emoji
                )
            ]
            await Database.ReactionRole.create(msg.id, options)

            await ctx.respond("✅ Done !", delete_after=5, ephemeral=True)
        except HTTPException:
            await ctx.respond(
                embed=EtherEmbeds.error(_("Emoji not found!")),
                ephemeral=True,
                delete_after=5,
            )
