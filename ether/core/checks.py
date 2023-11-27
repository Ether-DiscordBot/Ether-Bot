import discord


def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 398763512052056064
