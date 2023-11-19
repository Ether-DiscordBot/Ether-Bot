import discord
from discord import Message, NotFound, Role, app_commands
from discord.app_commands import Choice
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands import Context

from ether.core.constants import Emoji, Other
from ether.core.db.client import Database, ReactionRole
from ether.core.embed import Embed, ErrorEmbed
from ether.core.i18n import _


class Reactions(commands.Cog, name="reaction"):
    def __init__(self, client) -> None:
        self.help_icon = Emoji.REACTIONS
        self.client = client

    reaction = app_commands.Group(
        name="reaction", description="Reaction related commands"
    )

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

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if self.client.user.id != Other.MAIN_CLIENT_ID:
            return

        reactions = ReactionRole.from_guild(guild.id)
        if reactions:
            await reactions.delete()

    @reaction.command(name="add")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.rename(_type="type")
    @app_commands.describe(_type="Reaction type")
    @app_commands.choices(
        _type=[
            Choice(name="normal", value=0),  # Add or remove role
            Choice(name="unique", value=1),  # Only one role per messages
            Choice(name="verify", value=2),  # Claim one time for ever
            Choice(name="drop", value=3),  # Can only remove role
        ]
    )
    async def add(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: Role,
        _type: Choice[int] = 0,
    ):
        """Add a reaction role to a message"""

        try:
            msg: Message = await interaction.channel.fetch_message(message_id)
        except NotFound:
            return await interaction.response.send_message(
                embed=ErrorEmbed(_("Message not found!")),
                ephemeral=True,
                delete_after=5,
            )

        try:
            await msg.add_reaction(emoji)
            option = Database.ReactionRole.ReactionRoleOption.create(
                role_id=role.id, reaction=emoji
            )
            await Database.ReactionRole.update_or_create(
                message_id=msg.id,
                guild_id=interaction.guild.id,
                option=option,
                _type=_type,
            )

            await interaction.response.send_message(
                "✅ Done !", delete_after=5, ephemeral=True
            )
        except HTTPException:
            await interaction.response.send_message(
                embed=ErrorEmbed(_("Emoji not found!")),
                ephemeral=True,
                delete_after=5,
            )
