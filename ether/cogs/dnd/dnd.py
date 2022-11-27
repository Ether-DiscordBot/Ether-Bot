import requests

from discord import ApplicationContext, Embed, Option, OptionChoice, SlashCommandGroup
from discord.ext import commands

from ether.core.utils import EtherEmbeds
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


class DnD(commands.Cog, name="dnd"):
    DND_API_URL = "https://www.dnd5eapi.co/api/"

    def __init__(self, client) -> None:
        self.help_icon = Emoji.DND
        self.client = client

    dnd = SlashCommandGroup("dnd", "Dungeon & Dragons commands!")

    _class = dnd.create_subgroup("class", "Class commands!")

    @_class.command(name="infos")
    @locale_doc
    async def infos(
        self,
        ctx: ApplicationContext,
        _class: Option(
            str,
            name="class",
            description="Pick a class",
            choices=[
                OptionChoice("Barbarian", value="barbarian"),
                OptionChoice("Bard", value="bard"),
                OptionChoice("Clearic", value="cleric"),
                OptionChoice("Druid", value="druid"),
                OptionChoice("Fighter", value="fighter"),
                OptionChoice("Monk", value="monk"),
                OptionChoice("Paladin", value="paladin"),
                OptionChoice("Ranger", value="ranger"),
                OptionChoice("Rogue", value="rogue"),
                OptionChoice("Sorcerer", value="sorcerer"),
                OptionChoice("Warlock", value="warlock"),
                OptionChoice("Wizard", value="wizard"),
            ],
        ),
    ):
        """Get information about a class"""
        r = requests.get(f"{DnD.DND_API_URL}classes/{_class}")
        if not r.ok:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error was occured!")
            )

        class_data = r.json()

        primary_abilities = [
            ab["ability_score"]["name"]
            for ab in class_data["multi_classing"]["prerequisites"]
        ]
        embed = Embed(
            title=class_data["name"],
            url=f"https://www.dndbeyond.com/classes/{_class}",
            description=f"As a {class_data['name'].lower()}, you gain the following features.\n\n **Primary abilities:** {', '.join(primary_abilities)}",
        )

        embed.add_field(
            name="🎯 Hit Points",
            value=f" - **Hit Dice:** 1d{class_data['hit_die']} per {class_data['name'].lower()} level\n - **Hit points at 1st Level:** {class_data['hit_die']} + your Constitution modifier",
            inline=False,
        )
        proficiencies = [pro["name"] for pro in class_data["proficiencies"]]
        embed.add_field(
            name="📖 Proficiencies", value=f"{', '.join(proficiencies)}", inline=False
        )
        skills = [
            skill["name"][7:] for skill in class_data["proficiency_choices"][0]["from"]
        ]
        embed.add_field(
            name="💪 Skills",
            value=f"Choose two from {', '.join(skills)}",
            inline=False,
        )
        sub_classes = [sub["name"] for sub in class_data["subclasses"]]
        embed.add_field(name="🗂️ Sub classes", value=f"{', '.join(sub_classes)}")

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        await ctx.respond(embed=embed)

    @_class.command(name="spells")
    @locale_doc
    async def spells(
        self,
        ctx: ApplicationContext,
        _class: Option(
            str,
            name="class",
            description="Pick a class",
            choices=[
                OptionChoice("Barbarian", value="barbarian"),
                OptionChoice("Bard", value="bard"),
                OptionChoice("Clearic", value="cleric"),
                OptionChoice("Druid", value="druid"),
                OptionChoice("Fighter", value="fighter"),
                OptionChoice("Monk", value="monk"),
                OptionChoice("Paladin", value="paladin"),
                OptionChoice("Ranger", value="ranger"),
                OptionChoice("Rogue", value="rogue"),
                OptionChoice("Sorcerer", value="sorcerer"),
                OptionChoice("Warlock", value="warlock"),
                OptionChoice("Wizard", value="wizard"),
            ],
        ),
    ):
        """Get information about spell from a class"""
        r = requests.get(f"{DnD.DND_API_URL}classes/{_class}/spells")
        if not r.ok:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error was occured!")
            )

        spells_data = r.json()
        spells_list = [
            f"[{s['name']}](https://dndbeyond.com/spells/{s['index']})"
            for s in spells_data["results"]
        ]

        embed = Embed(
            title=f"{_class.capitalize()}' spells",
            url=f"https://dndbeyond.com/spells/class/{_class}",
        )
        embed.description = f"List of all {_class}'s spells: \n\n {', '.join(spells_list[:50])}{'...' if len(spells_list) > 50 else '.'}"
        if not spells_list:
            embed.description = "Not smart enough to use spells :/"

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        await ctx.respond(embed=embed)

    @dnd.command(name="spell")
    @locale_doc
    async def spell(self, ctx: ApplicationContext, spell: str):
        """Get informations about a spell"""
        spell = spell.lower().replace(" ", "-")

        r = requests.get(f"{DnD.DND_API_URL}spells/{spell}")

        if r.status_code == 404:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, I don't found your spell!")
            )
        elif not r.ok:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error was occured!")
            )

        spell_data = r.json()

        embed = Embed(
            title=f"{spell_data['name']} spell",
            url=f"https://www.dndbeyond.com/spells/{spell_data['index']}",
        )
        embed.description = f"{spell_data['desc'][0]}\n**Level:** {spell_data['level']}\n**Duration:** {spell_data['duration']}\n **Range/Area:** {spell_data['range']}\n **Casting Time:** {spell_data['casting_time']}"

        classes = [c["name"] for c in spell_data["classes"]]
        embed.add_field(name="🎓 Classes", value=f"{', '.join(classes)}", inline=False)
        sub_classes = [sub["name"] for sub in spell_data["subclasses"]]
        embed.add_field(
            name="🗂️ Sub classes", value=f"{', '.join(sub_classes)}", inline=False
        )

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        await ctx.respond(embed=embed)
