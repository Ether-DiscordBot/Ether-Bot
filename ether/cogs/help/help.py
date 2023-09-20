import discord
from discord import Embed, ApplicationContext, ComponentType, SelectOption
from discord.ext import commands, pages

from ether.core.i18n import _
from ether.core.constants import Emoji, Links, Other
from ether.core.logging import log


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.cooldown = commands.CooldownMapping(
            type=commands.BucketType.user, original=commands.Cooldown(1, 5)
        )

        self.show_hidden = False
        self.verify_checks = True
        self.help_icon = ""
        self.big_icon = ""
        self.message = None

        self.owner_cogs = ["Owner"]
        self.admin_cogs = ["Admin"]
        self.ignore_cogs = ["Help", "Event", "PlaylistEvent", "MusicEvent", "Reddit"]

    @commands.slash_command(name="help")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def help(self, ctx: ApplicationContext):
        """Help command"""
        extensions, desc_array, options = [], [], []

        for ext in set(self.client.cogs.values()):
            if ext.qualified_name in self.ignore_cogs:
                continue
            if ext.qualified_name in self.owner_cogs and not await ctx.bot.is_owner(
                ctx.author
            ):
                continue
            if (
                ext.qualified_name in self.admin_cogs
                and not await ctx.author.guild_permissions.administrator
            ):
                continue
            extensions.append(ext.qualified_name)

        extensions.sort()
        for ext in extensions:
            cog = self.client.get_cog(ext)
            desc_array.append(f"{cog.help_icon} **{cog.qualified_name}**")
            options.append(
                discord.SelectOption(
                    label=cog.qualified_name,
                    emoji=cog.help_icon if cog.help_icon else None,
                )
            )

        embed = Embed(
            description=f"{Emoji.DISCORD} [Support]({Links.SUPPORT_SERVER_URL}) | \
                      {Emoji.ETHER_ROUND} [Bot Invite]({Links.BOT_INVITE_URL}) | \
                      {Emoji.GITHUB} [Source code]({Links.BOT_SOURCE_CODE_URL})"
        )

        author = await self.client.fetch_user(Other.AUTHOR_ID)
        if author:
            embed.description += (
                f"\n\n**Made by:** [{author}](https://discord.com/users/{author.id})"
            )

        embed.set_author(
            icon_url=self.client.user.avatar.url, name=f"{self.client.user.name} Help"
        )
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.add_field(name="Categories:", value="\n".join(desc_array) + "\n\u200b")

        if ctx.guild:
            embed.set_footer(
                text="You can also navigate through the dropdown below to view commands in each category."
            )

        options.append(discord.SelectOption(label="Stop", emoji="🛑"))
        menu = discord.ui.Select(
            select_type=discord.ComponentType.string_select,
            options=options,
            placeholder="Choose a category...",
        )
        menu.callback = self.callback
        view = discord.ui.View(menu)

        return await ctx.respond(embed=embed, view=view)

    def build_cog_response(self, cog):
        commands = []
        cog = self.client.get_cog(cog)

        if not cog:
            return

        for cmd in cog.get_commands():
            if isinstance(cmd, discord.commands.core.SlashCommandGroup):
                for sub_cmd in cmd.walk_commands():
                    brief = (
                        "No information."
                        if not sub_cmd.description
                        else sub_cmd.description
                    )
                    commands.append(f"`/{sub_cmd.qualified_name}` - {brief}\n")

        embeds = []

        for i in range(0, len(commands), 25):
            embeds.append(
                Embed(
                    title=f"{cog.help_icon} {cog.qualified_name} commands",
                    description="".join(commands[i : i + 25]),
                )
            )

        if len(embeds) > 1:
            return pages.Paginator(
                pages=embeds, show_disabled=False, show_indicator=True
            )

        return embeds[0]

    async def callback(self, interaction: discord.Interaction):
        category = interaction.data["values"][0]
        paginator = self.build_cog_response(category)

        if paginator:
            return await interaction.response.edit_message(embed=paginator)
        return await interaction.response.edit_message(
            embed=Embed(description="Interaction closed."), delete_after=5
        )

    async def error_callback(self, error, item, _interaction):
        log.warning(f"Error in help command: {error} with item: {item}")
