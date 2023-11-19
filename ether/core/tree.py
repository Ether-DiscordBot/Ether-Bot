import discord
import wavelink
from discord import HTTPException, app_commands

from ether.core.embed import ErrorEmbed
from ether.core.logging import log


class Tree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await interaction.response.send_message(
                embed=ErrorEmbed(
                    description=f"This command is on cooldown, please retry in `{error.retry_after:.2f}s`."
                ),
                ephemeral=True,
            )

        ignored = (
            app_commands.NoPrivateMessage,
            # app_commands.DisabledCommand,
            app_commands.CheckFailure,
            app_commands.CommandNotFound,
            # app_commands.UserInputError,
            HTTPException,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        await interaction.response.send_message(
            embed=ErrorEmbed(
                description=f"An error occurred while executing this command, please retry later.\n If the problem persist, please contact the support.\n\n Error: `{error.__class__.__name__}({error})`"
            ),
            ephemeral=True,
        )

        log.error(f"Error on command {interaction.command.name}")
        log.error(f" => Selected parameters: {str(interaction.command.parameters)}")
        log.exception(error)
