from typing import Optional
import requests

from discord import ApplicationContext, Embed, Option, OptionChoice, SlashCommandGroup
from discord.ext import commands

from ether.core.utils import EtherEmbeds
from ether.core.constants import Emoji


class DnD(commands.Cog, name="dnd"):
    DND_API_URL = "https://www.dnd5eapi.co/api/"

    def __init__(self, client) -> None:
        self.help_icon = Emoji.DND
        self.client = client

    dnd = SlashCommandGroup("dnd", "Dungeon & Dragons commands!")

    _class = dnd.create_subgroup("class", "Class commands!")

    @_class.command(name="infos")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_infos(
        self,
        ctx: ApplicationContext,
        _class: Option(
            str,
            name="class",
            description="Pick a class",
            choices=[
                OptionChoice("Barbarian", value="barbarian"),
                OptionChoice("Bard", value="bard"),
                OptionChoice("Cleric", value="cleric"),
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

        embed = Embed(
            title=class_data["name"], url=f"https://www.dndbeyond.com/classes/{_class}"
        )

        embed.description = f"Hit die: {class_data['hit_die']}"

        # Proficiency choices
        proficiency_choices_desc = ""

        for prof_choice in class_data["proficiency_choices"]:
            proficiency_choices_desc += "- " + prof_choice["desc"] + "\n"

        embed.add_field(
            name="Proficiency choices",
            value=proficiency_choices_desc,
            inline=False,
        )

        # Proficiencies

        proficiencies = []
        for proficiency in class_data["proficiencies"]:
            if proficiency["index"].startswith("saving-throw"):
                continue
            proficiencies.append(proficiency["name"])

        proficiencies_desc = ", ".join(proficiencies)

        embed.add_field(
            name="Proficiencies",
            value=proficiencies_desc,
            inline=False,
        )

        # Saving throws
        saving_throws = []
        for saving_throw in class_data["saving_throws"]:
            saving_throws.append(saving_throw["name"])

        saving_throws_desc = ", ".join(saving_throws)

        embed.add_field(
            name="Saving throws",
            value=saving_throws_desc,
            inline=False,
        )

        # Starting equipment
        if len(class_data["starting_equipment"]) > 0:
            starting_equipment = []
            for equipement in class_data["starting_equipment"]:
                starting_equipment.append(
                    f"- {equipement['quantity']} x **{equipement['equipment']['name']}**"
                )

            starting_equipment_desc = "\n".join(starting_equipment)

            embed.add_field(
                name="Starting equipment",
                value=starting_equipment_desc,
                inline=False,
            )

        # Starting equipment options
        if len(class_data["starting_equipment_options"]) > 0:
            starting_equipment_options = []
            for starting_equipment_option in class_data["starting_equipment_options"]:
                starting_equipment_options.append(
                    "- " + starting_equipment_option["desc"]
                )

            starting_equipment_options_desc = "\n".join(starting_equipment_options)

            embed.add_field(
                name="Starting equipment options",
                value=starting_equipment_options_desc,
                inline=False,
            )

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        # Subclasses
        subclasses = []
        for subclass in class_data["subclasses"]:
            subclasses.append(subclass["name"])

        subclasses_desc = ", ".join(subclasses)

        embed.add_field(
            name="Subclasses",
            value=subclasses_desc,
            inline=False,
        )

        return await ctx.respond(embed=embed)

    @_class.command(name="levels")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_levels(
        self,
        ctx: ApplicationContext,
        _class: Option(
            str,
            name="class",
            description="Pick a class",
            choices=[
                OptionChoice("Barbarian", value="barbarian"),
                OptionChoice("Bard", value="bard"),
                OptionChoice("Cleric", value="cleric"),
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
        level: Optional[int] = -1,
    ):
        r = requests.get(f"{DnD.DND_API_URL}classes/{_class}/levels")
        if not r.ok:
            return await ctx.respond(
                embed=EtherEmbeds.error("Sorry, an error was occured!")
            )

        levels_data = r.json()

        embed = Embed(
            title=f"{_class.capitalize()}'s levels",
            url=f"https://dndbeyond.com/classes/{_class}#The{_class.capitalize()}Table",
        )

        if level >= 0:
            if len(levels_data) < level:
                return await ctx.respond(
                    embed=EtherEmbeds.error(
                        "Sorry, there is no information about this level!"
                    )
                )
            levels_data = [levels_data[level - 1]]

        for level in levels_data:
            level_desc = ""

            level_desc += f"- Ability score bonuses: {level['ability_score_bonuses']}\n"
            level_desc += f"- Proficiency bonus: {level['prof_bonus']}\n"

            # Features
            if len(level["features"]) > 0:
                features = []
                for feature in level["features"]:
                    features.append(feature["name"])

                features_desc = ", ".join(features)
                level_desc += f"- Features: {features_desc}\n\n"

            # Spellcasting
            if "spellcasting" in level:
                spellcasting = level["spellcasting"]
                level_desc += f"- Spellcasting:\n"

                if "cantrips_known" in spellcasting:
                    level_desc += (
                        f" - *Cantrips known:* {spellcasting['cantrips_known']}\n"
                    )
                if "spells_known" in spellcasting:
                    level_desc += f" - *Spells known:* {spellcasting['spells_known']}\n"
                for i in range(1, 9):
                    if (
                        f"spell_slots_level_{i}" in spellcasting
                        and spellcasting[f"spell_slots_level_{i}"] > 0
                    ):
                        level_desc += f" - *Spell slots level {i}:* {spellcasting[f'spell_slots_level_{i}']}\n"

            embed.add_field(
                name=f"Level {level['level']}",
                value=level_desc,
                inline=False,
            )

        return await ctx.respond(embed=embed, ephemeral=len(levels_data) >= 0)

    @_class.command(name="spells")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_spells(
        self,
        ctx: ApplicationContext,
        _class: Option(
            str,
            name="class",
            description="Pick a class",
            choices=[
                OptionChoice("Barbarian", value="barbarian"),
                OptionChoice("Bard", value="bard"),
                OptionChoice("Cleric", value="cleric"),
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

        return await ctx.respond(embed=embed)

    @dnd.command(name="spells")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def spells(self, ctx: ApplicationContext, spell: Optional[str] = None):
        """Get informations about a spell or a list of all spells"""
        if not spell:
            r = requests.get(f"{DnD.DND_API_URL}spells")
            if not r.ok:
                return await ctx.respond(
                    embed=EtherEmbeds.error("Sorry, an error was occured!")
                )

            spells_data = r.json()
            spells_list = [
                f"[{s['name']}](https://dndbeyond.com/spells/{s['index']})"
                for s in spells_data["results"]
            ]

            embed = Embed("Spells list")
            embed.description = f"List of all spells: \n\n {', '.join(spells_list[:100])}{'...' if len(spells_list) > 100 else '.'}"

            return await ctx.respond(embed=embed)

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

        return await ctx.respond(embed=embed)

    @commands.is_owner()
    @dnd.command(name="test")
    async def test(self, ctx: ApplicationContext):
        cls = [
            "barbarian",
            "bard",
            "cleric",
            "druid",
            "fighter",
            "monk",
            "paladin",
            "ranger",
            "rogue",
            "sorcerer",
            "warlock",
            "wizard",
        ]

        for cl in cls:
            await ctx.invoke(self.class_infos, cl)
            await ctx.invoke(self.class_levels, cl)
            await ctx.invoke(self.class_spells, cl)

        await ctx.invoke(self.spells, "acid-arrow")
