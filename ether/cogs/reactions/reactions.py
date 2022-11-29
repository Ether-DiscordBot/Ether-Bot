from discord import (
    ApplicationContext,
    Message,
    NotFound,
    Role,
    SlashCommandGroup,
    Option,
    OptionChoice,
)
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
            if matchs_emojis:
                role = payload.member.guild.get_role(matchs_emojis[0].role_id)
                channel = payload.member.guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(message_id)
                msg_reaction = [
                    r
                    for r in message.reactions
                    if r.emoji == payload.emoji.name
                    or (r.is_custom_emoji() and r.emoji.name == payload.emoji.name)
                ][0]

                match reaction._type:
                    case 0:  # normal
                        await payload.member.add_roles(role)
                    case 1:  # unique
                        for r in message.reactions:
                            users = await r.users().flatten()
                            member_matchs = [
                                m for m in users if m.id == payload.member.id
                            ]
                            if member_matchs:
                                for m in member_matchs:
                                    if r.emoji != msg_reaction.emoji:
                                        await r.remove(m)
                        await payload.member.add_roles(role)
                    case 2:  # verify
                        await msg_reaction.remove(payload.member)
                        await payload.member.add_roles(role)
                    case 3:  # drop
                        await payload.member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        emoji = payload.emoji.name

        reaction = await ReactionRole.from_id(message_id)
        if reaction:
            matchs_emojis = [e for e in reaction.options if e.reaction == emoji]
            if matchs_emojis:
                guild = self.client.get_guild(payload.guild_id)
                role = guild.get_role(matchs_emojis[0].role_id)

                member = guild.get_member(payload.user_id)

                match reaction._type:
                    case 0:  # normal
                        await member.remove_roles(role)
                    case 1:  # unique
                        await member.remove_roles(role)
                    case 2:  # verify
                        pass
                    case 3:  # drop
                        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        r_message = await ReactionRole.from_id(payload.message_id)
        if r_message:
            await r_message.delete()

    @reactions.command()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(
        self,
        ctx: ApplicationContext,
        message_id: str,
        emoji: str,
        role: Role,
        _type: Option(
            int,
            name="type",
            description="Reaction type",
            choices=[
                OptionChoice(name="normal", value=0),  # Add or remove role
                OptionChoice(name="unique", value=1),  # Only one role per messages
                OptionChoice(name="verify", value=2),  # Claim one time for ever
                OptionChoice(name="drop", value=3),  # Can only remove role
            ],
        ) = 0,
    ):
        """Add a reaction role to a message"""

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
            option = Database.ReactionRole.ReactionRoleOption.create(
                role_id=role.id, reaction=emoji
            )
            await Database.ReactionRole.update_or_create(
                message_id=msg.id, option=option, _type=_type
            )

            await ctx.respond("✅ Done !", delete_after=5, ephemeral=True)
        except HTTPException:
            await ctx.respond(
                embed=EtherEmbeds.error(_("Emoji not found!")),
                ephemeral=True,
                delete_after=5,
            )
