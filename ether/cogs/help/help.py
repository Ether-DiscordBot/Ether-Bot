import discord
from discord import Embed
from discord.ext import commands, pages
from pycord18n.extension import _

from ether.core.i18n import locale_doc


class Help(discord.Cog):
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

        self.owner_cogs = []
        self.admin_cogs = ["Admin"]
        self.ignore_cogs = ["Help", "Reactions"]

    @commands.slash_command(name="help")
    @locale_doc
    async def help(self, ctx):
        """Help command"""
        extensions, desc_array, options = [], [], []

        for ext in set(self.client.cogs.values()):
            if ext.qualified_name in self.ignore_cogs:
                continue
            # if ext.qualified_name in self.owner_cogs and not await ctx.author.guild_permissions.administrator:
            #     continue
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
                discord.SelectOption(label=cog.qualified_name, emoji=cog.help_icon)
            )

        embed = Embed()
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
        menu = discord.ui.Select(options=options, placeholder="Choose a category...")
        menu.callback = self.callback
        view = discord.ui.View(menu, timeout=180.0, disable_on_timeout=True)

        return await ctx.respond(embed=embed, view=view)

    def build_cog_response(self, cog):
        commands = []
        cog = self.client.get_cog(cog)

        for cmd in cog.get_commands():
            brief = "No information." if cmd.short_doc is None else cmd.short_doc
            commands.append(f"{cmd.qualified_name} - {brief}\n")

        embeds = []

        for i in range(0, len(commands), 25):
            embeds.append(
                Embed(
                    title=f"{cog.help_icon} {cog.qualified_name} Commands",
                    description="".join(commands[i : i + 25]),
                )
            )

        group = pages.PageGroup(
            pages=embeds,
            label="Page Group Test",
            description="page group test",
            timeout=180.0,
            disable_on_timeout=True,
        )
        return pages.Paginator(group=group, show_menu=True)

    async def callback(self, interaction):
        category = interaction.data["values"][0]
        paginator = self.build_cog_response(category)

        await paginator.respond(interaction, ephemeral=False)
