import discord
from discord import app_commands

from ether.core.embed import Embed
from ether.core.logging import log


class Tree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await interaction.response.send_message(
                embed=Embed.error(
                    description=f"This command is on cooldown, please retry in `{error.retry_after:.2f}s`."
                ),
                ephemeral=True,
            )

        ignored = (
            app_commands.NoPrivateMessage,
            app_commands.CheckFailure,
            app_commands.CommandNotFound,
            discord.errors.HTTPException,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        await interaction.response.send_message(
            embed=Embed.error(
                description=f"An error occurred while executing this command, please retry later.\n If the problem persist, please contact the support.\n\n Error: `{error.__class__.__name__}({error})`"
            ),
            ephemeral=True,
        )

        if interaction.command:
            parameters_display = [p.display_name for p in interaction.command.parameters]
            log.error(f"Error on command {interaction.command.name}")
            log.error(f" => Selected parameters: {', '.join(parameters_display)}")
        log.exception(error)
