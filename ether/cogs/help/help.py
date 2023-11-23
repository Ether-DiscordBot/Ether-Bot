import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, Paginator

from ether.core.constants import Emoji, Links, Other
from ether.core.embed import Embed
from ether.core.i18n import _
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
        self.ignore_cogs = ["Help", "Event", "PlaylistEvent", "MusicEvent"]

    @app_commands.command(name="help")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def help(self, interaction: discord.Interaction):
        """Help command"""
        extensions, desc_array, options = [], [], []

        app_info = await interaction.client.application_info()

        for ext in set(self.client.cogs.values()):
            if ext.qualified_name in self.ignore_cogs:
                continue
            if (
                ext.qualified_name in self.owner_cogs
                and app_info.owner.id != interaction.user.id
            ):
                continue
            if (
                ext.qualified_name in self.admin_cogs
                and not await interaction.user.guild_permissions.administrator
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

        if interaction.guild:
            embed.set_footer(
                text="You can also navigate through the dropdown below to view commands in each category."
            )

        # Changelog field
        with open("CHANGELOG.md", "r") as f:
            lines = f.readlines()

            content = "".join(lines)
            content = content.split("##", 2)[1]

            split = content.strip().split('\n', 1)

            title = f"New in version {split[0]}"
            description = split[1]


        embed.add_field(name=title, value=description)


        options.append(discord.SelectOption(label="Stop", emoji="🛑"))
        menu = discord.ui.Select(
            options=options,
            placeholder="Choose a category...",
        )
        menu.callback = self.callback
        view = discord.ui.View()
        view.add_item(menu)

        return await interaction.response.send_message(embed=embed, view=view)

    def build_cog_response(self, cog_name):
        cmds = []
        cog: commands.Cog = self.client.get_cog(cog_name)

        if not cog:
            return

        def get_brief(cmd: app_commands.Command):
            return (
                "No information."
                if not cmd.description
                else cmd.description
            )

        for cmd in cog.walk_app_commands():
            if isinstance(cmd, app_commands.Group):
                for sub_cmd in cmd.walk_commands():
                    cmds.append(f"`/{sub_cmd.qualified_name}` - {get_brief(sub_cmd)}\n")
                continue

            cmds.append(f"`/{cmd.qualified_name}` - {get_brief(cmd)}\n")

        embeds = [
            Embed(
                title=f"{cog.help_icon} {cog.qualified_name} commands",
                description="".join(cmds[i : i + 25]),
            )
            for i in range(0, len(cmds), 25)
        ]
        if len(embeds) > 1:
            return Paginator(pages=embeds, show_disabled=False, show_indicator=True)

        return embeds[0]

    async def callback(self, interaction: discord.Interaction):
        category = interaction.data["values"][0]
        if paginator := self.build_cog_response(category):
            return await interaction.response.edit_message(embed=paginator)
        return await interaction.response.edit_message(
            embed=Embed(description="Interaction closed."), delete_after=5
        )

    async def error_callback(self, error, item, _interaction):
        log.warning(f"Error in help command: {error} with item: {item}")
